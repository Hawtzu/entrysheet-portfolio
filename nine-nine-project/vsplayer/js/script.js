const boardSize = 9;
const board = document.getElementById("board");
const rollDiceButton = document.getElementById("rollDice");
const diceResult = document.getElementById("diceResult");
const turnIndicator = document.getElementById("turnIndicator");
let isPlayer1SkillSelected = false;
let isPlayer2SkillSelected = false;


let playerPositions = {
    1: { x: 0, y: 4 },
    2: { x: 8, y: 4 }
};
let currentPlayer = 1;
let stones = [];
let diceValue = 0;
let temporaryButtons = [];

let nextDiceValues = {
    1: Math.floor(Math.random() * 4) + 1,
    2: Math.floor(Math.random() * 4) + 1
};

let playerPoints = {
    1: 0,
    2: 0
};

// 盤面を作成
function createBoard() {
    board.innerHTML = "";
    for (let y = 0; y < boardSize; y++) {
        for (let x = 0; x < boardSize; x++) {
            const cell = document.createElement("div");
            cell.dataset.x = x;
            cell.dataset.y = y;
            cell.className = "grid";

            if (playerPositions[1].x === x && playerPositions[1].y === y) {
                cell.textContent = "P1";
                cell.classList.add("player1");
            } else if (playerPositions[2].x === x && playerPositions[2].y === y) {
                cell.textContent = "P2";
                cell.classList.add("player2");
            } else if (stones.some(stone => stone.x === x && stone.y === y)) {
                cell.textContent = "S";
                cell.classList.add("stone");
            }

            board.appendChild(cell);
        }
    }
}

// サイコロを振る
function rollDice() {
    // 現在のサイコロの目を取得
    const currentDiceValue = nextDiceValues[currentPlayer];

    // 次のサイコロの目を更新
    nextDiceValues[currentPlayer] = Math.floor(Math.random() * 4) + 1;

    // 現在のサイコロの目を表示
    const currentDiceElement = document.getElementById(`player${currentPlayer}-current-dice`);
    currentDiceElement.textContent = `現在のサイコロの目: ${currentDiceValue}`;
    
    // 現在のサイコロの目をターンに応じて色付け
    if (currentPlayer === 1) {
        currentDiceElement.style.color = "blue";
    } else if (currentPlayer === 2) {
        currentDiceElement.style.color = "red";
    }

    // 次のサイコロの目を表示
    document.getElementById(`player${currentPlayer}-next-dice`).textContent = `次のサイコロの目: ${nextDiceValues[currentPlayer]}`;

    // 他プレイヤーの現在のサイコロの目を "-" に戻す
    const otherPlayer = currentPlayer === 1 ? 2 : 1;
    const otherDiceElement = document.getElementById(`player${otherPlayer}-current-dice`);
    otherDiceElement.textContent = `現在のサイコロの目: -`;
    otherDiceElement.style.color = "black"; // 他プレイヤーの色をリセット

    updatePhaseIndicator("移動フェーズ");
    updateDiceDisplay(currentDiceValue);

    diceValue = currentDiceValue; // 現在のサイコロの目を反映
    promptDirection(); // 移動方向を選択
}

function promptDirection() {
    const validDirections = getValidDirections();



    // デバッグ用ログ
    console.log("選択可能な方向:", validDirections);

    // 選べる方向に応じてポイントを獲得
    const pointsEarned = calculatePoints(validDirections);
    playerPoints[currentPlayer] += pointsEarned;
    document.getElementById(`player${currentPlayer}-points`).textContent = `ポイント: ${playerPoints[currentPlayer]}`;
    if (pointsEarned > 0) {
        showPointEffect(currentPlayer, pointsEarned);
    }

    if (validDirections.length === 0) {
        alert(`プレイヤー${currentPlayer}は移動できません。敗北です。`);
        resetGame();
        return;
    }

    // 一時的な方向ボタンを表示
    displayTemporaryButtons(validDirections, (selectedDirection) => {
        console.log("選択された方向:", selectedDirection.name); // デバッグ用ログ
        movePlayer(selectedDirection.name, diceValue);
    });
}


function movePlayer(direction, steps) {
    clearTemporaryButtons(); // 一時的なボタンを消去

    // 現在のプレイヤーの位置を取得
    let { x, y } = playerPositions[currentPlayer];

    // デバッグ用ログ
    console.log(`=== 移動開始 ===`);
    console.log(`現在の位置: (${x}, ${y})`);
    console.log(`選択された方向: ${direction}`);
    console.log(`サイコロの目: ${steps}`);

    // 移動処理
    for (let i = 0; i < steps; i++) {
        // 次に移動しようとする位置
        let nextX = x;
        let nextY = y;

        if (direction === "up") nextY--;
        if (direction === "down") nextY++;
        if (direction === "left") nextX--;
        if (direction === "right") nextX++;

        console.log(`移動予定の位置: (${nextX}, ${nextY})`);

        // 画面外の場合は敗北
        if (isOutOfBounds(nextX, nextY)) {
            console.log("移動停止: 画面外に出たため敗北");
            alert(`プレイヤー${currentPlayer}の敗北です！`);
            resetGame();
            return;
        }

        // 石がある場合は停止
        if (isStone(nextX, nextY)) {
            console.log("移動停止: 石に衝突");
            break;
        }

        // 他のプレイヤーがいる場合は停止
        if (isPlayer(nextX, nextY)) {
            console.log("移動停止: 他のプレイヤーに衝突");
            break;
        }

        // 移動が有効な場合、現在の位置を更新
        x = nextX;
        y = nextY;
        console.log(`移動中: (${x}, ${y})`);
    }

    // 最終的な位置をプレイヤーの位置に反映
    playerPositions[currentPlayer] = { x, y };

    // デバッグ用ログ
    console.log(`移動後の位置: (${x}, ${y})`);
    console.log(`=== 移動終了 ===`);

    // 盤面を再描画
    createBoard();

    // 石の配置に進む
    promptStonePlacement();
}
// 石を配置
function promptStonePlacement() {
    const validPositions = getValidStonePositions();
    updatePhaseIndicator("石置きフェーズ");

    // サイコロの目は石置きフェーズでも同じ
    updateDiceDisplay(diceValue);
    
    // デバッグ用ログ
    console.log("選択可能な石の配置方向:", validPositions);

    // 選べる方向に応じてポイントを獲得
    const pointsEarned = calculatePoints(validPositions);
    playerPoints[currentPlayer] += pointsEarned;
    document.getElementById(`player${currentPlayer}-points`).textContent = `ポイント: ${playerPoints[currentPlayer]}`;
    if (pointsEarned > 0) {
        showPointEffect(currentPlayer, pointsEarned);
    }

    if (validPositions.length === 0) {
        alert("石を置ける場所がありません。");
        endTurn();
        return;
    }

    displayTemporaryButtons(validPositions, (selectedPosition) => {
        stones.push(selectedPosition);
        createBoard();
        endTurn();
    });
}


// 一時的なボタンを表示
function displayTemporaryButtons(options, callback) {
    clearTemporaryButtons(); // 既存のボタンを消去

    options.forEach(option => {
        const button = document.createElement("button");
        button.textContent = option.label || "";
        button.className = "temp-button";
        button.style.gridRowStart = option.y + 1;
        button.style.gridColumnStart = option.x + 1;

        button.addEventListener("click", () => {
            clearTemporaryButtons();
            callback(option); // オブジェクト全体ではなく方向名など特定のプロパティを渡す
        });

        board.appendChild(button);
        temporaryButtons.push(button);
    });
}

// 一時的なボタンを消去
function clearTemporaryButtons() {
    temporaryButtons.forEach(button => button.remove());
    temporaryButtons = [];
}

// 有効な移動方向を取得
function getValidDirections() {
    const { x, y } = playerPositions[currentPlayer];
    const directions = [
        { name: "up", x, y: y - 1, label: "↑" },
        { name: "down", x, y: y + 1, label: "↓" },
        { name: "left", x: x - 1, y, label: "←" },
        { name: "right", x: x + 1, y, label: "→" }
    ];

    return directions.filter(dir => !isOutOfBounds(dir.x, dir.y) && !isStone(dir.x, dir.y) && !isPlayer(dir.x, dir.y));
}

// 有効な石の配置場所を取得
function getValidStonePositions() {
    const { x, y } = playerPositions[currentPlayer];
    const positions = [
        { x, y: y - 1, label: "↑" },
        { x, y: y + 1, label: "↓" },
        { x: x - 1, y, label: "←" },
        { x: x + 1, y, label: "→" }
    ];
    return positions.filter(pos => !isOutOfBounds(pos.x, pos.y) && !isStone(pos.x, pos.y) && !isPlayer(pos.x, pos.y));
}

// ターンを終了
function endTurn() {
    currentPlayer = currentPlayer === 1 ? 2 : 1;
    turnIndicator.textContent = `ターン: プレイヤー${currentPlayer}`;
    updatePhaseIndicator("待機中");
    updateDiceDisplay("-");
    startTurn(); // 次のターンを開始
}

// ターンを開始
function startTurn() {
    console.log("=== ターン開始: startTurn 関数呼び出し ===");
    console.log(`現在のプレイヤー: ${currentPlayer}`);

    playerPoints[currentPlayer] += 10;
    document.getElementById(`player${currentPlayer}-points`).textContent = `ポイント: ${playerPoints[currentPlayer]}`;

    rollDice();
    updateSkillButtons();

    console.log("=== ターン終了: startTurn 関数終了 ===");
}


function calculatePoints(availableDirections) {
    const directionCount = availableDirections.length;
    if (directionCount === 4) return 0;
    if (directionCount === 3) return 0;
    if (directionCount === 2) return 5;
    if (directionCount === 1) return 10;
    return 0; // 方向が選べない場合はポイントなし
}

function showPointEffect(player, points) {
    const pointElement = document.getElementById(`player${player}-points`);
    const effectElement = document.createElement("span");

    effectElement.textContent = ` +${points}`;
    effectElement.style.color = "green";
    effectElement.style.fontSize = "14px";
    effectElement.style.marginLeft = "10px";
    effectElement.style.transition = "opacity 1s ease";
    effectElement.style.opacity = "1";

    pointElement.appendChild(effectElement);

    // 1秒後にエフェクトを消す
    setTimeout(() => {
        effectElement.style.opacity = "0";
        setTimeout(() => effectElement.remove(), 1000); // 完全に消去
    }, 1000);
}

function updatePhaseIndicator(phase) {
    const phaseIndicator = document.getElementById("phaseIndicator");
    phaseIndicator.textContent = `フェーズ: ${phase}`;
}

function updateDiceDisplay(value) {
    const diceDisplay = document.getElementById("diceDisplay");
    diceDisplay.textContent = `サイコロの目: ${value}`;
}

function useSkill1() {
    if (playerPoints[currentPlayer] >= 100) {
        playerPoints[currentPlayer] -= 100;
        diceValue += 1; // サイコロの目を1増やす
        document.getElementById(`player${currentPlayer}-points`).textContent = `ポイント: ${playerPoints[currentPlayer]}`;
        updateDiceDisplay(diceValue); // サイコロの表示を更新
        updateSkillButtons(); // ボタンの有効化/無効化を再チェック
        alert(`プレイヤー${currentPlayer}が共通スキル1を使用しました！サイコロの目: ${diceValue}`);
    }
}

function useSkill2() {
    if (playerPoints[currentPlayer] >= 100 && diceValue > 1) {
        playerPoints[currentPlayer] -= 100;
        diceValue -= 1; // サイコロの目を1減らす
        document.getElementById(`player${currentPlayer}-points`).textContent = `ポイント: ${playerPoints[currentPlayer]}`;
        updateDiceDisplay(diceValue); // サイコロの表示を更新
        updateSkillButtons(); // ボタンの有効化/無効化を再チェック
        alert(`プレイヤー${currentPlayer}が共通スキル2を使用しました！サイコロの目: ${diceValue}`);
    }
}

function updateSkillButtons() {
    const skill1Button = document.getElementById("skill1");
    const skill2Button = document.getElementById("skill2");

    console.log(`現在のプレイヤー: ${currentPlayer}`);
    console.log(`ポイント: ${playerPoints[currentPlayer]}`);
    console.log(`現在のサイコロの目: ${diceValue}`);

    // 共通スキル1のボタン状態
    skill1Button.disabled = playerPoints[currentPlayer] < 100;

    // 共通スキル2のボタン状態
    skill2Button.disabled = playerPoints[currentPlayer] < 100 || diceValue <= 1;

    // ボタンのスタイルを更新
    skill1Button.classList.toggle("enabled", !skill1Button.disabled);
    skill2Button.classList.toggle("enabled", !skill2Button.disabled);

    console.log(`スキル1有効: ${!skill1Button.disabled}`);
    console.log(`スキル2有効: ${!skill2Button.disabled}`);
}



// 初期化
function resetGame() {
    playerPositions = {
        1: { x: 0, y: 4 },
        2: { x: 8, y: 4 }
    };
    stones = [];
    playerPoints = { 1: 0, 2: 0 }; // ポイントをリセット
    currentPlayer = 1;
    document.getElementById(`player1-points`).textContent = `ポイント: ${playerPoints[1]}`;
    document.getElementById(`player2-points`).textContent = `ポイント: ${playerPoints[2]}`;
    document.getElementById(`player1-next-dice`).textContent = `次のサイコロの目: ${nextDiceValues[1]}`;
    document.getElementById(`player2-next-dice`).textContent = `次のサイコロの目: ${nextDiceValues[2]}`;
    document.getElementById(`player1-current-dice`).textContent = `現在のサイコロの目: -`;
    document.getElementById(`player2-current-dice`).textContent = `現在のサイコロの目: -`;
    turnIndicator.textContent = "ターン: プレイヤー1";
    createBoard();
    startTurn(); // 初期化後に最初のターンを開始
}


// ヘルパー関数
function isOutOfBounds(x, y) {
    return x < 0 || x >= boardSize || y < 0 || y >= boardSize;
}

function isStone(x, y) {
    return stones.some(stone => stone.x === x && stone.y === y);
}

function isPlayer(x, y) {
    return Object.entries(playerPositions).some(([player, pos]) => {
        // 現在のプレイヤーを除外して判定
        if (parseInt(player) === currentPlayer) return false;
        return pos.x === x && pos.y === y;
    });
}


const skillList = [
    { name: "子", description: "100ポイントでサイコロの目を1に変更", icon: "assets/icons/zodiac-rat-icon.png", cost: 100 }
];


let player1SkillIndex = 0;
let player2SkillIndex = 0;

// スキルを切り替える関数
function updateSkillDisplay(player, skillIndex) {
    const skill = skillList[skillIndex];
    document.getElementById(`${player}-skill-icon`).src = skill.icon;
    document.getElementById(`${player}-skill-name`).textContent = skill.name;
    document.getElementById(`${player}-skill-desc`).textContent = skill.description;
}

// 矢印ボタンのイベントリスナー
document.querySelector(".prev-skill").addEventListener("click", () => {
    player1SkillIndex = (player1SkillIndex - 1 + skillList.length) % skillList.length;
    updateSkillDisplay("player1", player1SkillIndex);
});

document.querySelector(".next-skill").addEventListener("click", () => {
    player1SkillIndex = (player1SkillIndex + 1) % skillList.length;
    updateSkillDisplay("player1", player1SkillIndex);
});



// プレイヤー2用矢印ボタンのイベントリスナー
document.querySelector("#right-skill-area .prev-skill").addEventListener("click", () => {
    player2SkillIndex = (player2SkillIndex - 1 + skillList.length) % skillList.length;
    updateSkillDisplay("player2", player2SkillIndex);
});

document.querySelector("#right-skill-area .next-skill").addEventListener("click", () => {
    player2SkillIndex = (player2SkillIndex + 1) % skillList.length;
    updateSkillDisplay("player2", player2SkillIndex);
});

// スキルボタンの有効・無効を更新
function updateSkillButton(player) {
    const skillButton = document.getElementById(`player${player}-skill-button`);
    const skill = skillList[player === 1 ? player1SkillIndex : player2SkillIndex];

    if (playerPoints[player] >= skill.cost) {
        skillButton.disabled = false; // ボタンを有効化
        skillButton.style.opacity = "1"; // 見た目の強調
        skillButton.style.cursor = "pointer";
    } else {
        skillButton.disabled = true; // ボタンを無効化
        skillButton.style.opacity = "0.5"; // 見た目を薄く
        skillButton.style.cursor = "not-allowed";
    }
}


// プレイヤー1のスキル確定処理
document.getElementById("confirm-player1-skill").addEventListener("click", () => {
    alert(`プレイヤー1のスキルが「${skillList[player1SkillIndex].name}」に決まりました！`);
    isPlayer1SkillSelected = true;

    // ボタン切り替え
    const confirmButton = document.getElementById("confirm-player1-skill");
    confirmButton.style.display = "none";

    const skillButton = document.createElement("button");
    skillButton.id = "player1-skill-button";
    skillButton.classList.add("skill-button");
    skillButton.textContent = `${skillList[player1SkillIndex].name} 発動 (${skillList[player1SkillIndex].cost}ポイント)`;
    confirmButton.parentNode.appendChild(skillButton);

    // スキルボタン初期状態を更新
    updateSkillButton(1);

    skillButton.addEventListener("click", () => {
        if (selectedSkills[1] === "子") {
            useSkillZodiac();
        }
    });

    if (isPlayer1SkillSelected && isPlayer2SkillSelected) {
        startGame();
    }
});

// プレイヤー2のスキル確定処理
document.getElementById("confirm-player2-skill").addEventListener("click", () => {
    alert(`プレイヤー2のスキルが「${skillList[player2SkillIndex].name}」に決まりました！`);
    isPlayer2SkillSelected = true;

    // ボタン切り替え
    const confirmButton = document.getElementById("confirm-player2-skill");
    confirmButton.style.display = "none";

    const skillButton = document.createElement("button");
    skillButton.id = "player2-skill-button";
    skillButton.classList.add("skill-button");
    skillButton.textContent = `${skillList[player2SkillIndex].name} 発動 (${skillList[player2SkillIndex].cost}ポイント)`;
    confirmButton.parentNode.appendChild(skillButton);

    // スキルボタン初期状態を更新
    updateSkillButton(2);

    skillButton.addEventListener("click", () => {
        if (selectedSkills[2] === "子") {
            useSkillZodiac();
        }
    });

    if (isPlayer1SkillSelected && isPlayer2SkillSelected) {
        startGame();
    }
});



// スキル「子」の効果
function useSkillZodiac() {
    if (playerPoints[currentPlayer] < 100) {
        alert("ポイントが足りません！");
        return;
    }

    // ポイント消費
    playerPoints[currentPlayer] -= 100;
    document.getElementById(`player${currentPlayer}-points`).textContent = `ポイント: ${playerPoints[currentPlayer]}`;

    // サイコロの目を1に変更
    diceValue = 1;
    document.getElementById(`player${currentPlayer}-current-dice`).textContent = `現在のサイコロの目: ${diceValue}`;
    alert(`スキル「子」を使用しました！サイコロの目が1に変更されました。`);
}



function startGame() {
    alert("両プレイヤーのスキルが決定しました。ゲームを開始します！");
    resetGame();
}


// 初期化


document.getElementById("skill1").addEventListener("click", useSkill1);
document.getElementById("skill2").addEventListener("click", useSkill2);

document.getElementById("confirm-player1-skill").addEventListener("click", () => {
    if (selectedSkills[1] === "子") {
        document.querySelector("#left-skill-area .skill-box button").addEventListener("click", useSkillZodiac);
    }
});

document.getElementById("confirm-player2-skill").addEventListener("click", () => {
    if (selectedSkills[2] === "子") {
        document.querySelector("#right-skill-area .skill-box button").addEventListener("click", useSkillZodiac);
    }
});
