import numpy as np

import kornia
import torch
import torch.nn as nn
import torch.nn.functional as F
import utils


class ReplayBuffer(object):
    """Buffer to store environment transitions."""

    def __init__(self, obs_shape, action_shape, capacity, image_pad, device, effective_aug):
        self.capacity = capacity
        self.device = device
        self.effective_aug = effective_aug
        self.aug_trans = nn.Sequential(
            nn.ReplicationPad2d(image_pad),
            kornia.augmentation.RandomCrop((obs_shape[-1], obs_shape[-1])))

        self.obses = np.empty((capacity, *obs_shape), dtype=np.uint8)
        self.next_obses = np.empty((capacity, *obs_shape), dtype=np.uint8)
        self.actions = np.empty((capacity, *action_shape), dtype=np.float32)
        self.rewards = np.empty((capacity, 1), dtype=np.float32)
        self.not_dones = np.empty((capacity, 1), dtype=np.float32)
        self.not_dones_no_max = np.empty((capacity, 1), dtype=np.float32)
        # HosH begin
        self.priorities = np.empty((capacity, 1), dtype=np.float32)
        # HosH end
        self.idx = 0
        self.full = False
        self.clip_max = 110.0
        self.initial_priority = 10000
    def __len__(self):
        return self.capacity if self.full else self.idx

    def add(self, obs, action, reward, next_obs, done, done_no_max):
        np.copyto(self.obses[self.idx], obs)
        np.copyto(self.actions[self.idx], action)
        np.copyto(self.rewards[self.idx], reward)
        np.copyto(self.next_obses[self.idx], next_obs)
        np.copyto(self.not_dones[self.idx], not done)
        np.copyto(self.not_dones_no_max[self.idx], not done_no_max)
        # HosH begins
        np.copyto(self.priorities[self.idx],
                  self.initial_priority)  # (at the beginning we should not do augmentation so set a priority a relatively high number)
        # HosH ends
        self.idx = (self.idx + 1) % self.capacity
        self.full = self.full or self.idx == 0

    # HosH begins
    def update_priorities(self, idxs, priorities):
        priorities = priorities.detach().cpu().numpy()
        for i, var in enumerate(idxs):
            self.priorities[var] = priorities[i]

    # HosH ends

    def sample(self, batch_size, logger, step):
        idxs = np.random.randint(0,
                                 self.capacity if self.full else self.idx,
                                 size=batch_size)

        obses = self.obses[idxs]
        next_obses = self.next_obses[idxs]
        obses_aug = obses.copy()
        next_obses_aug = next_obses.copy()
        original_obses = obses.copy()
        original_next_obses = next_obses.copy()
        priority = self.priorities[idxs]

        obses = torch.as_tensor(obses, device=self.device).float()
        next_obses = torch.as_tensor(next_obses, device=self.device).float()
        obses_aug = torch.as_tensor(obses_aug, device=self.device).float()
        next_obses_aug = torch.as_tensor(next_obses_aug,
                                         device=self.device).float()
        original_obses = torch.as_tensor(original_obses, device=self.device).float()
        original_next_obses = torch.as_tensor(original_next_obses, device=self.device).float()

        actions = torch.as_tensor(self.actions[idxs], device=self.device)
        rewards = torch.as_tensor(self.rewards[idxs], device=self.device)
        not_dones_no_max = torch.as_tensor(self.not_dones_no_max[idxs],
                                           device=self.device)

        obses = self.aug_trans(obses)
        next_obses = self.aug_trans(next_obses)

        obses_aug = self.aug_trans(obses_aug)
        next_obses_aug = self.aug_trans(next_obses_aug)

        if self.effective_aug:
            # p = np.clip(np.squeeze(priority), a_min=0.0, a_max=self.clip_max)
            highest_error = np.argsort(np.squeeze(priority))[batch_size - 3:batch_size]
            not_augmented_ctr = 0
            for i in range(batch_size):
                if (i in highest_error) or (priority[i] == self.initial_priority):  # replace the augmented with original images
                    obses[i] = original_obses[i]
                    next_obses[i] = original_next_obses[i]
                    obses_aug[i] = original_obses[i]
                    next_obses_aug[i] = original_next_obses[i]
                    not_augmented_ctr += 1
            # rnd = np.random.randint(0,4)
            # for j in range(rnd):
            #     i = np.random.randint(1,batch_size-1)
            #     obses[i] = original_obses[i]
            #     next_obses[i] = original_next_obses[i]
            #     obses_aug[i] = original_obses[i]
            #     next_obses_aug[i] = original_next_obses[i]
            #     not_augmented_ctr += 1
            logger.log('train/augmented_observations', batch_size - not_augmented_ctr, step)
        return obses, actions, rewards, next_obses, not_dones_no_max, obses_aug, next_obses_aug, idxs
