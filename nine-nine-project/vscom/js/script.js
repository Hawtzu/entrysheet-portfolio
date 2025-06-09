const boardSize = 9;
const board = document.getElementById('board');
const diceResult = document.getElementById('diceResult');
const rollDiceButton = document.getElementById('rollDice');
const fiveOptions = document.getElementById('fiveOptions');
const turnIndicator = document.getElementById('turnIndicator'); // ターン表示用の要素
const turnCount = document.getElementById('turnCount'); // ターン数表示用の要素
const timerElement = document.getElementById('timer'); // タイマー表示用の要素
let playerPosition = { x: 4, y: 8 };  // 自分のキャラの初期位置 (下辺の真ん中)
let enemyPosition = { x: 4, y: 0 };   // 相手のキャラの初期位置 (上辺の真ん中)
let stones = [];
let currentPlayer = 'player';  // 現在のターンを管理
let turnNumber = 1; // ターン数を管理
let timer; // タイマーのインターバルID
let timeRemaining = 5 * 60; // 5分（300秒）
let currentDiceValue = null;
let moveCallback = null;
let stoneCallback = null;
let fiveOptionCallback = null;

// 盤面を作成
function createBoard() {
    board.innerHTML = '';
    for (let y = 0; y < boardSize; y++) {
        for (let x = 0; x < boardSize; x++) {
            const cell = document.createElement('div');
            if (x === playerPosition.x && y === playerPosition.y) {
                cell.textContent = 'P';  // 自分のキャラ
                cell.style.backgroundColor = 'lightgreen';
            } else if (x === enemyPosition.x && y === enemyPosition.y) {
                cell.textContent = 'E';  // 相手のキャラ
                cell.style.backgroundColor = 'lightcoral';
            } else if (stones.some(stone => stone.x === x && stone.y === y)) {
                cell.textContent = 'S';  // 石
                cell.style.backgroundColor = 'gray';
            }
            board.appendChild(cell);
        }
    }
}

// 現在のターンを更新する関数
function updateTurnIndicator() {
    turnIndicator.textContent = `ターン: ${currentPlayer === 'player' ? 'プレイヤー' : '敵'}`;
    turnCount.textContent = `ターン数: ${turnNumber}`; // ターン数を更新
}

// タイマーを更新する関数
function updateTimer() {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    timerElement.textContent = `残り時間: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    if (timeRemaining > 0) {
        timeRemaining--;
    } else {
        alert('時間切れです。ゲームオーバーです。');
        initGame();
    }
}

// ゲーム初期化
function initGame() {
    playerPosition = { x: 4, y: 8 };  // 自分のキャラの初期位置 (下辺の真ん中)
    enemyPosition = { x: 4, y: 0 };   // 相手のキャラの初期位置 (上辺の真ん中)
    stones = [];
    currentPlayer = Math.random() < 0.5 ? 'player' : 'enemy';  // 先攻後攻をランダムに決定
    turnNumber = 1; // ゲームを初期化した時点ではターン数は１
    timeRemaining = 5 * 60; // タイマーをリセット
    clearInterval(timer); // 既存のタイマーをクリア
    timer = setInterval(updateTimer, 1000); // タイマーを開始
    createBoard();
    diceResult.textContent = 'サイコロの目: -';
    setDirectionButtonsEnabled(false);
    fiveOptions.style.display = 'none';
    
    updateTurnIndicator();
    updateDiceResultBackground();

    if (currentPlayer === 'player') {
        playerTurn();
    } else {
        setTimeout(enemyTurn, 1000);  // 少し遅延を入れて敵のターンを開始
    }   
}

// サイコロの目の背景色を現在のプレイヤーに応じて更新する関数
function updateDiceResultBackground() {
    if (currentPlayer === 'player') {
        diceResult.classList.add('player');
        diceResult.classList.remove('enemy');
    } else {
        diceResult.classList.add('enemy');
        diceResult.classList.remove('player');
    }
}


// サイコロを振る
function rollDice() {
    const result = Math.floor(Math.random() * 5) + 1;
    diceResult.textContent = `サイコロの目: ${result}`;
    updateDiceResultBackground(); // 背景色を更新
    return result;
}

// 指定した方向の1マス目に石があるかをチェックする関数
function isStoneInDirection(direction, position = playerPosition) {
    const { x, y } = position;
    let nextX = x;
    let nextY = y;

    if (direction === 'up') nextY--;
    else if (direction === 'down') nextY++;
    else if (direction === 'left') nextX--;
    else if (direction === 'right') nextX++;

    return stones.some(stone => stone.x === nextX && stone.y === nextY);
}

// 指定した方向の1マス目にキャラがいるかをチェックする関数
function isCharacterInDirection(direction, position = playerPosition) {
    const { x, y } = position;
    let nextX = x;
    let nextY = y;

    if (direction === 'up') nextY--;
    else if (direction === 'down') nextY++;
    else if (direction === 'left') nextX--;
    else if (direction === 'right') nextX++;

    return (nextX === playerPosition.x && nextY === playerPosition.y) ||
           (nextX === enemyPosition.x && nextY === enemyPosition.y);
}

// 指定した方向の１マス目が移動可能かを確認する関数
function canMove(direction,position) {
    if (isStoneInDirection(direction, position) || isCharacterInDirection(direction, position)) {
        return false;
    }

    let { x, y } = position;
    if (direction === 'up') y--;
    else if (direction === 'down') y++;
    else if (direction === 'left') x--;
    else if (direction === 'right') x++;

    // その方向の１マス目が崖の場合はflase
    if (x < 0 || x >= boardSize || y < 0 || y >= boardSize) {
        return false;
    }

    return true;
}

// 全ての方向に移動可能かを確認する関数
function canMoveAnyDirection(position = playerPosition) {
    return canMove('up', position) || canMove('down', position) ||
           canMove('left', position) || canMove('right', position);
}

// 指定した方向に石を置けるかを確認する関数
function canPlaceStone(direction, position = playerPosition) {
    const { x, y } = position;
    let nextX = x;
    let nextY = y;

    if (direction === 'up') nextY--;
    else if (direction === 'down') nextY++;
    else if (direction === 'left') nextX--;
    else if (direction === 'right') nextX++;
    else if (direction === 'up-left') { nextX--; nextY--; }
    else if (direction === 'up-right') { nextX++; nextY--; }
    else if (direction === 'down-left') { nextX--; nextY++; }
    else if (direction === 'down-right') { nextX++; nextY++; }

    if (nextX < 0 || nextX >= boardSize || nextY < 0 || nextY >= boardSize) {
        return false;
    }

    if (stones.some(stone => stone.x === nextX && stone.y === nextY) ||
        (nextX === playerPosition.x && nextY === playerPosition.y) ||
        (nextX === enemyPosition.x && nextY === enemyPosition.y)) {
        return false;
    }

    return true;
}

// 全ての方向に石を置けるかを確認する関数
function canPlaceStoneAnyDirection(position = playerPosition) {
    return canPlaceStone('up', position) || canPlaceStone('down', position) ||
           canPlaceStone('left', position) || canPlaceStone('right', position) ||
           canPlaceStone('up-left', position) || canPlaceStone('up-right', position) ||
           canPlaceStone('down-left', position) || canPlaceStone('down-right', position);
}

// キャラクターの移動
function movePlayer(direction, steps) {
    if (!canMove(direction,playerPosition)) {
        alert('その方向には移動できません');
        return false;
    }

    let { x, y } = playerPosition;
    for (let i = 0; i < steps; i++) {
        if (direction === 'up') y--;
        else if (direction === 'down') y++;
        else if (direction === 'left') x--;
        else if (direction === 'right') x++;

        if (x < 0 || x >= boardSize || y < 0 || y >= boardSize) {
            if (currentDiceValue === 4) {
                // サイコロの目が4の場合、崖から落ちない
                if (direction === 'up') y++;
                else if (direction === 'down') y--;
                else if (direction === 'left') x++;
                else if (direction === 'right') x--;
                break;
            } else {
                alert('崖から落ちてしまいました。ゲームオーバーです。');
                initGame();
                return false;
            }
        }

        if (stones.some(stone => stone.x === x && stone.y === y) ||
            (x === playerPosition.x && y === playerPosition.y) ||
            (x === enemyPosition.x && y === enemyPosition.y)) {
            // 石またはキャラにぶつかったら停止
            if (direction === 'up') y++;
            else if (direction === 'down') y--;
            else if (direction === 'left') x++;
            else if (direction === 'right') x--;
            break;
        }
    }
    playerPosition = { x, y };
    createBoard();
    return true;
}

// 石を置く音を鳴らす関数
function playStoneSound() {
    const stoneSound = document.getElementById('stoneSound');
    stoneSound.play();
}



// 石を置く
function placeStone(direction) {
    const { x, y } = playerPosition;
    let stonePosition;

    switch (direction) {
        case 'up':
            stonePosition = { x, y: y - 1 };
            break;
        case 'down':
            stonePosition = { x, y: y + 1 };
            break;
        case 'left':
            stonePosition = { x: x - 1, y };
            break;
        case 'right':
            stonePosition = { x: x + 1, y };
            break;
        case 'up-left':
            stonePosition = { x: x - 1, y: y - 1 };
            break;
        case 'up-right':
            stonePosition = { x: x + 1, y: y - 1 };
            break;
        case 'down-left':
            stonePosition = { x: x - 1, y: y + 1 };
            break;
        case 'down-right':
            stonePosition = { x: x + 1, y: y + 1 };
            break;
        default:
            alert('無効な方向です。');
            return false;  // 置けない場合もfalseを返すように修正
    }

    if (stonePosition.x < 0 || stonePosition.x >= boardSize || stonePosition.y < 0 || stonePosition.y >= boardSize) {
        alert('盤面外に石を置くことはできません。');
        return false;  // 置けない場合もfalseを返すように修正
    }

    if (stones.some(stone => stone.x === stonePosition.x && stone.y === stonePosition.y) ||
        (stonePosition.x === playerPosition.x && stonePosition.y === playerPosition.y) ||
        (stonePosition.x === enemyPosition.x && stonePosition.y === enemyPosition.y)) {
        alert('既に石が置かれている場所またはキャラがいる場所には置けません。');
        return false;  // 置けない場合もfalseを返すように修正
    }

    stones.push(stonePosition);
    createBoard();
    playStoneSound();  // 石を置く音を鳴らす
    endTurn();  // ターンの終了を呼び出す
    return true;  // 置けた場合はtrueを返す
}

// プレイヤーのターンを開始する関数
function playerTurn() {
    rollDiceButton.style.visibility = 'visible';
}

// 敵のその方向への移動が安全か確認する関数
function safeMove(direction, position, diceValue) {
    if (!canMove(direction, position)) {
        return false;
    }

    let { x, y } = position;
    for (let i = 0; i < diceValue; i++) {
        if (direction === 'up') y--;
        else if (direction === 'down') y++;
        else if (direction === 'left') x--;
        else if (direction === 'right') x++;

        // 崖に落ちる場合は移動不可
        if (x < 0 || x >= boardSize || y < 0 || y >= boardSize) {
            return diceValue === 4;
        }

        // ２マス目以降に石またはキャラにぶつかって止まったかどうかの判断。これは移動できているのでtrue
        if (stones.some(stone => stone.x === x && stone.y === y) ||
            (x === playerPosition.x && y === playerPosition.y) ||
            (x === enemyPosition.x && y === enemyPosition.y)) {
            return true;
        }
    }
    return true;
}


function enemyTurn() {
    // サイコロを振る
    currentDiceValue = rollDice();

    // 1秒後に敵の移動を行う
    setTimeout(() => {
        if (currentDiceValue === 5) {
            // 5が出た場合の処理
            const choice = Math.random() < 0.5 ? 1 : 2;
            if (choice === 1) {
                // 選択肢１：普通に5マス移動する選択
                let moveDirections = ['up', 'down', 'left', 'right'].filter(direction => safeMove(direction, enemyPosition, currentDiceValue));
                if (moveDirections.length === 0) {
                    alert('1の選択肢を選びましたが崖から落ちるので2の選択肢を実行します。');
                    placeEnemyStoneRandomly();
                    return;
                }
                let moveDirection = moveDirections[Math.floor(Math.random() * moveDirections.length)];
                moveEnemy(moveDirection, currentDiceValue);
            } else {
                // 選択肢２：移動をスキップして石を置く選択
                placeEnemyStoneRandomly();
                return;
            }
        } else {
            // 5以外の目が出た場合の処理
            let moveDirections = ['up', 'down', 'left', 'right'].filter(direction => safeMove(direction, enemyPosition, currentDiceValue));
            if (moveDirections.length === 0) {
                alert('敵は全ての方向に移動できません。あなたの勝利です.');
                initGame();
                return;
            }
            let moveDirection = moveDirections[Math.floor(Math.random() * moveDirections.length)];
            moveEnemy(moveDirection, currentDiceValue);
        }

        // 1秒後に石を置く処理を行う
        setTimeout(() => {
            let stoneDirections = ['up', 'down', 'left', 'right'].filter(direction => canPlaceStone(direction, enemyPosition));
            if (stoneDirections.length === 0) {
                alert('敵は全ての方向に石を置けません。あなたの勝利です。');
                initGame();
                return;
            }
            let stoneDirection = stoneDirections[Math.floor(Math.random() * stoneDirections.length)];
            placeEnemyStone(stoneDirection);
            return;
        }, 1000); // 1秒の間隔を追加

    }, 1000); // サイコロを振った後に1秒の間隔を追加
}

// 敵がランダムに石を置く処理を行う関数
function placeEnemyStoneRandomly() {
    let stoneDirections = ['up', 'down', 'left', 'right', 'up-left', 'up-right', 'down-left', 'down-right'].filter(direction => canPlaceStone(direction, enemyPosition));
    if (stoneDirections.length === 0) {
        alert('敵は全ての方向に石を置けません。あなたの勝利です。');
        initGame();
        return;
    }
    let stoneDirection = stoneDirections[Math.floor(Math.random() * stoneDirections.length)];
    placeEnemyStone(stoneDirection);
}


// 敵の移動を処理する関数
function moveEnemy(direction, steps) {
    let { x, y } = enemyPosition;
    for (let i = 0; i < steps; i++) {
        if (direction === 'up') y--;
        else if (direction === 'down') y++;
        else if (direction === 'left') x--;
        else if (direction === 'right') x++;
        
        if (x < 0 || x >= boardSize || y < 0 || y >= boardSize) {
            if (currentDiceValue === 4) {
                if (direction === 'up') y++;
                else if (direction === 'down') y--;
                else if (direction === 'left') x++;
                else if (direction === 'right') x--;
                break;
            } else {
                alert('敵が崖から落ちました。あなたの勝利です。');
                initGame();
                return;
            }
        }

        if (stones.some(stone => stone.x === x && stone.y === y) ||
            (x === playerPosition.x && y === playerPosition.y) ||
            (x === enemyPosition.x && y === enemyPosition.y)) {
            if (direction === 'up') y++;
            else if (direction === 'down') y--;
            else if (direction === 'left') x++;
            else if (direction === 'right') x--;
            break;
        }
    }
    enemyPosition = { x, y };
    createBoard();
}

// 敵が石を置く処理をする関数
function placeEnemyStone(direction) {
    const { x, y } = enemyPosition;
    let stonePosition;

    switch (direction) {
        case 'up':
            stonePosition = { x, y: y - 1 };
            break;
        case 'down':
            stonePosition = { x, y: y + 1 };
            break;
        case 'left':
            stonePosition = { x: x - 1, y };
            break;
        case 'right':
            stonePosition = { x: x + 1, y };
            break;
        case 'up-left':
            stonePosition = { x: x - 1, y: y - 1 };
            break;
        case 'up-right':
            stonePosition = { x: x + 1, y: y - 1 };
            break;
        case 'down-left':
            stonePosition = { x: x - 1, y: y + 1 };
            break;
        case 'down-right':
            stonePosition = { x: x + 1, y: y + 1 };
            break;
        default:
            return;
    }

    stones.push(stonePosition);
    playStoneSound();  // 石を置く音を鳴らす
    createBoard();

    endTurn();  // ターンの終了を呼び出す
}

// ターンの終了処理
function endTurn() {
    currentPlayer = (currentPlayer === 'player') ? 'enemy' : 'player';
    turnNumber++;
    updateTurnIndicator();
    if (currentPlayer === 'player') {
        playerTurn();
    } else {
        setTimeout(enemyTurn, 1000);  // 少し遅延を入れて敵のターンを開始
    }
}

// 矢印ボタンの有効/無効を設定
function setDirectionButtonsEnabled(enabled, directions = []) {
    document.querySelectorAll('.direction').forEach(button => {
        if (enabled && (directions.length === 0 || directions.includes(button.dataset.direction))) {
            button.disabled = false;
        } else {
            button.disabled = true;
        }
    });
}

// 矢印ボタンのクリックイベント
document.querySelectorAll('.direction').forEach(button => {
    button.addEventListener('click', () => {
        const direction = button.dataset.direction;
        if (moveCallback) {
            moveCallback(direction);
            moveCallback = null;
        } else if (stoneCallback) {
            stoneCallback(direction);
            stoneCallback = null;
        }
    });
});

// 6が出たときの選択肢ボタンのクリックイベント
document.getElementById('option1').addEventListener('click', () => {
    if (fiveOptionCallback) {
        fiveOptionCallback(1);
        fiveOptionCallback = null;
    }
});

document.getElementById('option2').addEventListener('click', () => {
    if (fiveOptionCallback) {
        fiveOptionCallback(2);
        fiveOptionCallback = null;
    }
});

// イベントリスナーの設定
rollDiceButton.addEventListener('click', () => {
    rollDiceButton.style.visibility = 'hidden';  // visibilityを使用して非表示
    currentDiceValue = rollDice();
    setTimeout(() => {
        if (currentDiceValue <= 3) {
            if (!canMoveAnyDirection()) {
                alert('全ての方向に移動できません。敗北です。');
                initGame();
                return;
            }
            promptDirectionAndMove();  // 修正された部分
        } else if (currentDiceValue === 4) {
            if (!canMoveAnyDirection()) {
                alert('全ての方向に移動できません。敗北です。');
                initGame();
                return;
            }
            promptDirectionAndMove();  // 修正された部分
        } else if (currentDiceValue === 5) {
            fiveOptions.style.display = 'block';
            fiveOptionCallback = (choice) => {
                fiveOptions.style.display = 'none';
                if (choice === 1) {
                    if (!canMoveAnyDirection()) {
                        alert('全ての方向に移動できません。敗北です。');
                        initGame();
                        return;
                    }
                    promptDirectionAndMove();  // 修正された部分
                } else if (choice === 2) {
                    if (!canPlaceStoneAnyDirection()) {
                        alert('全ての方向に石を置けません。敗北です。');
                        initGame();
                        return;
                    }
                    promptDirectionAndPlaceStone(['up', 'down', 'left', 'right', 'up-left', 'up-right', 'down-left', 'down-right']);  // 6の場合の石を置く処理
                }
            };
        }
    }, 0);
});

// 移動方向を選んで移動するプロンプトを表示
function promptDirectionAndMove() {
    setDirectionButtonsEnabled(true, ['up', 'down', 'left', 'right']);
    moveCallback = (direction) => {
        if (!movePlayer(direction, currentDiceValue)) {
            setTimeout(promptDirectionAndMove, 0);  // 移動できなかった場合、再度プロンプトを表示
        } else {
            setTimeout(() => {
                if (!canPlaceStoneAnyDirection()) {
                    alert('全ての方向に石を置けません。敗北です。');
                    initGame();
                    return;
                }
                promptDirectionAndPlaceStone(['up', 'down', 'left', 'right']);  // 石を置くプロンプトを表示
            }, 0);  // 移動後に石を置く
        }
    };
}

// 石を置く方向を選んで置くプロンプトを表示
function promptDirectionAndPlaceStone(directions) {
    setDirectionButtonsEnabled(true, directions);
    stoneCallback = (direction) => {
        if (!placeStone(direction)) {
            setTimeout(() => promptDirectionAndPlaceStone(directions), 0);  // 置けなかった場合、再度プロンプトを表示
        } else {
            setDirectionButtonsEnabled(false);
        }
    };
}

// ゲームを初期化
initGame();
