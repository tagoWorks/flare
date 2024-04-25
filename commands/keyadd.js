const { SlashCommandBuilder } = require('@discordjs/builders');
const fs = require('fs');
const path = require('path');
const { ownerID, guildID } = require('../config.json');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('keyadd')
    .setDescription('Add a new key to the list of valid keys')
    .addStringOption(option =>
      option
        .setName('key')
        .setDescription('The activation key to add')
        .setRequired(true)
    )
    .addStringOption(option =>
      option
        .setName('lock')
        .setDescription('Type of license locker')
        .addChoices(
          { name: 'IP Address', value: 'IP' },
          { name: 'Machine HWID', value: 'HWID' }
        )
    ),
  async execute(interaction) {
    console.log('Received interaction:', interaction);

    if (interaction.user.id !== ownerID) {
      console.log('Unauthorized access attempted by user:', interaction.user.id);
      return interaction.reply({ content: 'You are not allowed to use this command.', ephemeral: true });
    }

    const licenseKeyToAdd = interaction.options.getString('key');
    const licenseLockType = interaction.options.getString('lock');
    console.log('Received license key to add:', licenseKeyToAdd);
    console.log('Received license lock type:', licenseLockType);

    const licenseFilePath = path.join(__dirname, '..', 'assets', 'validkeys.txt');
    console.log('Reading file from path:', licenseFilePath);
    
    fs.readFile(licenseFilePath, 'utf8', (err, data) => {
      if (err) {
        console.error('Error reading key file:', err);
        return interaction.reply({ content: 'Error adding key. Please try again later.', ephemeral: true });
      }

      console.log('Successfully read file data:', data);

      const existingKeys = data.trim().split('\n');
      console.log('Existing keys:', existingKeys);

      if (existingKeys.includes(licenseKeyToAdd)) {
        console.log('Key already exists:', licenseKeyToAdd);
        return interaction.reply({ content: 'This key already exists.', ephemeral: true });
      }

      const newKeyEntry = licenseLockType ? `${licenseKeyToAdd}:${licenseLockType}` : licenseKeyToAdd;
      console.log('New key entry:', newKeyEntry);

      const newData = data.trim() + (data.trim() ? '\n' : '') + newKeyEntry;
      console.log('Updated data:', newData);

      fs.writeFile(licenseFilePath, newData, (err) => {
        if (err) {
          console.error('Error adding key:', err);
          return interaction.reply({ content: 'Error adding key. Please try again later.', ephemeral: true });
        }

        console.log('Key added successfully:', licenseKeyToAdd);
        const licenseLockerMessage = licenseLockType ? ` with ${licenseLockType} lock` : '';
        return interaction.reply({ content: `Activation key ${licenseKeyToAdd}${licenseLockerMessage} added successfully.`, ephemeral: true });
      });
    });
  },
  defaultPermission: false,
  permissions: [
    { id: guildID, type: 'ROLE', permission: false },
    { id: ownerID, type: 'USER', permission: true },
  ],
};
