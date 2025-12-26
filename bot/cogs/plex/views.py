import discord


class PaginatorView(discord.ui.View):
    def __init__(self, ctx, pages):
        super().__init__(timeout=60)  # auto-disable after 60s of inactivity
        self.ctx = ctx
        self.pages = pages
        self.current_page = 0

    async def update_message(self, interaction: discord.Interaction):
        embed = self.pages[self.current_page]
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.gray)
    async def first_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = 0
        await self.update_message(interaction)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.blurple)
    async def previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self.update_message(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.blurple)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self.update_message(interaction)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.gray)
    async def last_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = len(self.pages) - 1
        await self.update_message(interaction)

    async def on_timeout(self):
        # disable all buttons when time runs out
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
