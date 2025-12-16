# **Connect 4 MCTS Bot**

A Connect 4 AI built using Monte Carlo Tree Search (MCTS).
This project is intended for validating an MCTS implementation before extending it toward an AlphaZero-style agent.

## **Features**

- Core MCTS implementation (selection, expansion, simulation, backpropagation)

- Semi-random rollouts that:

  - Take immediate winning moves

  - Block opponent wins when possible

- Console-based gameplay

- Configurable thinking time

- Configurable starting player

## **Notes on Performance**

- Plays fairly well, but is not perfect

- Given enough simulations, MCTS should approach optimal play

- Not optimized for speed or efficiency (clarity over performance)

## **Usage**

- To experiment with the bot, edit the following lines in the source code:

  - AI thinking time: **Modify line 10 to control how long the bot runs MCTS before choosing a move.**

  - Or alternativly, AI itterations: **Modify line 9 to control how many MCTS itterations the bot runs before choosing a move**

  - Starting player: **Toggle line 11 to change which player goes first.**

  - Advanced Settings: **Modify lines 7-8 to change MCTS settings.**


- The game state and moves are printed directly to the console.
