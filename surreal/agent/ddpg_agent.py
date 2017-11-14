"""
Actor function
"""
import torch
from torch.autograd import Variable
from .base import Agent, AgentMode
from surreal.model.ddpg_net import DDPGModel
import numpy as np


class DDPGAgent(Agent):

    def __init__(self,
                 learn_config,
                 env_config,
                 session_config,
                 agent_mode):
        super().__init__(learn_config, env_config, session_config, agent_mode)

        self.action_dim = self.env_config.action_spec.dim[0]
        self.obs_dim = self.env_config.obs_spec.dim[0]

        self.model = DDPGModel(
            obs_dim=self.obs_dim,
            action_dim=self.action_dim,
        )

        # Ornstein-Uhlenbeck noise for exploration
        self.use_ou_noise = False
        self.noise = torch.zeros(1, self.action_dim)

        self.logsig = -1.0

    def act(self, obs):

        assert torch.is_tensor(obs)
        obs = Variable(obs.unsqueeze(0))
        action = self.model.actor(obs)

        if self.agent_mode is not AgentMode.eval_deterministic:
            std = float(np.exp(self.logsig))
            noise_random = torch.zeros(1, self.action_dim).normal_(std=std)
            if self.use_ou_noise:
                self.noise = self.noise + noise_random
            else:
                self.noise = noise_random
            # self.noise.clamp_(-0.2, 0.2)

        action.data.add_(self.noise).clamp_(-1, 1)
        return action.data.numpy().squeeze()

    def module_dict(self):
        return {
            'ddpg': self.model,
        }

    def default_config(self):
        return {
            'model': {
                'convs': '_list_',
                'fc_hidden_sizes': '_list_',
            },
        }