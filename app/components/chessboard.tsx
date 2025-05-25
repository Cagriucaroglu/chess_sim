import React from "react";
import { Dimensions, Image, StyleSheet, View } from "react-native";
import BackGround from "./background";

export const pieceImages: Record<string, any> = {
    wp: require("../../assets/chesspieces/wp.png"),
    wr: require("../../assets/chesspieces/wr.png"),
    wn: require("../../assets/chesspieces/wn.png"),
    wb: require("../../assets/chesspieces/wb.png"),
    wq: require("../../assets/chesspieces/wq.png"),
    wk: require("../../assets/chesspieces/wk.png"),
    bp: require("../../assets/chesspieces/bp.png"),
    br: require("../../assets/chesspieces/br.png"),
    bn: require("../../assets/chesspieces/bn.png"),
    bb: require("../../assets/chesspieces/bb.png"),
    bq: require("../../assets/chesspieces/bq.png"),
    bk: require("../../assets/chesspieces/bk.png"),
}

interface IChessboardprop {
    fen: string; 
}

// const squareSize = 40;
// const boardSize = squareSize * 8;

const Chessboard = ({ fen}: IChessboardprop) => {
    const { width } = Dimensions.get("window");
    const boardSize = width - 15;
    const squareSize = boardSize / 8;
    const rows = fen.split(" ")[0].split("/");

    const styles = StyleSheet.create({
        container: {
            width: boardSize,
            height: boardSize,
            position: "relative",
            backgroundColor: "#b58863",
        },
        piece: {
            width: squareSize,
            height: squareSize,
            position: "absolute",
        },
    });

    return (
        <View style={styles.container}>
            <BackGround />
            {rows.map((row, rowIndex) => {
                let colIndex = 0;
                return (
                    <View key={`row-${rowIndex}`} style={styles.piece}>
                        {row.split("").map((char, index) => {
                            if (isNaN(Number(char))) {
                                const color = char === char.toUpperCase() ? "w" : "b";
                                const piece = color + char.toLowerCase();
                                const positionStyle = {
                                    left: colIndex * squareSize,
                                    top: rowIndex * squareSize,
                                };
                                colIndex++;
                                return (
                                    <Image
                                        key={`${rowIndex}-${colIndex}`}
                                        source={pieceImages[piece]}
                                        style={[styles.piece, positionStyle]}
                                    />
                                );
                            } else {
                                colIndex += parseInt(char);
                                return null;
                            }
                        })}
                    </View>
                );
            })}
        </View>
    );
};



export default Chessboard;
