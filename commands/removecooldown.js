const { SlashCommandBuilder } = require('@discordjs/builders');
const path = require('path');
const { cooldowns } = require('../events/shared.js');
const { ownerID, guildID } = require('../config.json');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('removecooldown')
    .setDescription('Remove cooldown for a user')
    .addUserOption(option =>
      option
        .setName('user')
        .setDescription('The user to remove cooldown for')
        .setRequired(true)
    ),
  async execute(interaction) {
    if (interaction.user.id !== ownerID) {
      return interaction.reply({ content: 'You do not have permission to use this command.', ephemeral: true });
    }
    const user = interaction.options.getUser('user');
    if (!user) {
      return interaction.reply({ content: 'Please provide a user to remove cooldown for.', ephemeral: true });
    }
    if (!cooldowns[user.id]) {
      return interaction.reply({ content: 'There is no cooldown set for the provided user.', ephemeral: true });
    }
    delete cooldowns[user.id];
    return interaction.reply({ content: `Cooldown removed successfully for user ${user.username}.`, ephemeral: true });
  },
  defaultPermission: false,
  permissions: [
    {
      id: guildID,
      type: 'ROLE',
      permission: false,
    },
    {
      id: ownerID,
      type: 'USER',
      permission: true,
    },
  ],
};