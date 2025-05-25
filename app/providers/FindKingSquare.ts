import { Chess } from "chess.js";

export function findKingSquare(chess:Chess, color:string) {
    const board = chess.board();
    for (let r = 0; r < 8; r++) {
        for (let f = 0; f < 8; f++) {
            const piece = board[r][f];
            if (piece && piece.type === 'k' && piece.color === color) {
                const file = 'abcdefgh'[f];
                const rank = 8 - r;
                return `${file}${rank}`;
            }
        }
    }
    return "";
}

export function findCheckingPieces(move: string)
{
    move = move.slice(0, -1);
    if (move[0] && move[0] === move[0].toUpperCase()) {
        move = move.slice(1);
    }
    if(move[0] && move[0] == "x"){
        move = move.slice(1);
    }
    return move;
}