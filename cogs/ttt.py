import discord
from discord.ext import commands
from typing import List

class Colours:
    standard = 0x2b2d31

class Emotes:
    warning = "⚠️"
    crown = "👑"

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToe = self.view
        if view.board[self.y][self.x] in (view.X, view.O):
            return  

        current_player = player1 if view.current_player == view.X else player2

        if interaction.user != current_player:
            embed = discord.Embed(
                color=Colours.standard,
                description=f"> {Emotes.warning} {interaction.user.mention}: it is not your turn yet"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return


        self.style = discord.ButtonStyle.danger if view.current_player == view.X else discord.ButtonStyle.success
        self.label = 'X' if view.current_player == view.X else 'O'
        self.disabled = True
        view.board[self.y][self.x] = view.current_player
        view.current_player = view.O if view.current_player == view.X else view.X


        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'> {Emotes.crown} {player1.mention} is the winner!'
            elif winner == view.O:
                content = f'> {Emotes.crown} {player2.mention} is the winner!'
            else:
                content = "It's a tie!"
            for child in view.children:
                child.disabled = True
            view.stop()
        else:
            content = f"{player2.mention if view.current_player == view.X else player1.mention}'s turn"

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [[0, 0, 0] for _ in range(3)]
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        for i in range(3):
            if sum(self.board[i]) == 3:
                return self.O
            if sum(self.board[i]) == -3:
                return self.X
        for j in range(3):
            if sum(self.board[i][j] for i in range(3)) == 3:
                return self.O
            if sum(self.board[i][j] for i in range(3)) == -3:
                return self.X
        if self.board[0][0] + self.board[1][1] + self.board[2][2] == 3:
            return self.O
        if self.board[0][2] + self.board[1][1] + self.board[2][0] == 3:
            return self.O
        if self.board[0][0] + self.board[1][1] + self.board[2][2] == -3:
            return self.X
        if self.board[0][2] + self.board[1][1] + self.board[2][0] == -3:
            return self.X
        if all(cell != 0 for row in self.board for cell in row):
            return self.Tie
        return None


class TicTacToeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ttt"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tictactoe(self, ctx, member: discord.Member = None):
        global player1, player2
        if member is None or member == ctx.author:
            embed = discord.Embed(
                color=Colours.standard,
                description=f"> {Emotes.warning} please mention a valid user."
            )
            await ctx.send(embed=embed)
            return

        player1 = member
        player2 = ctx.author
        await ctx.reply(f"{member.mention}'s turn", view=TicTacToe())

async def setup(bot) -> None:
    await bot.add_cog(TicTacToeCog(bot))
