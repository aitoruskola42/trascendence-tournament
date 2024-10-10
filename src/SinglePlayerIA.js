'use strict'

import { calculation } from "./iaCalc.js"

//Game variables
let canvas;
let ctx;
let player1Y, player2Y;
let ballX, ballY;

let ballIAX, ballIAY;

let ballSpeedX, ballSpeedY;
let player1Up, player1Down;
let player2Up, player2Down;
let gameLoopId;
let timeoutId;
let player1Score;
let player2Score;
let wait;
let finish;


//añadidos para IA
let IAstartTime = Date.now();
let lastDirection = null; // null para el inicio, 0 para arriba, 1 para abajo
let isAIRunning = false;
//let ballxIa, ballyIA;

//constants  
const BALL_SIZE = 10;
const PADDLE_SPEED = 6;
const PADDLE_HEIGHT = 100;
const PADDLE_WIDTH = 10;
const BALL_DIR_RIGHT = '+';
const BALL_DIR_LEFT = '-';
const BALL_DIR_UP = '-';
const BALL_DIR_DOWN = '+';
const SPEED_INC = 0.15;
const ANGLE_INC = 0.4;



export function initializeGameIA() {
	canvas = document.getElementById('pongCanvas');
	ctx = canvas.getContext('2d');
	setBallSpeed();
	player1Up = false;
	player1Down = false;
	player2Up = false;
	player2Down = false;
	player1Score = 0;
	player2Score = 0;
	wait = false;
	finish = false;
	


	// calculo para encontrar el punto medio de una superficie disponible
    player1Y = (canvas.height - PADDLE_HEIGHT) / 2;
    player2Y = (canvas.height - PADDLE_HEIGHT) / 2;
    ballX = canvas.width / 2 /*- BALL_SIZE / 2;*/
    ballY = canvas.height / 2 /*- BALL_SIZE / 2;*/

	ballIAX = ballX;
	ballIAY = ballY;

    document.addEventListener('keydown', (event) => {
		if (event.key === 'w') player1Up = true;
		if (event.key === 's') player1Down = true;
		//if (event.key === 'ArrowUp') player2Up = true;
		//if (event.key === 'ArrowDown') player2Down = true;
    });

    document.addEventListener('keyup', (event) => {
		if (event.key === 'w') player1Up = false;
		if (event.key === 's') player1Down = false;
		//if (event.key === 'ArrowUp') player2Up = false;
		//if (event.key === 'ArrowDown') player2Down = false;
    });
	


	if (!window.aiInterval) {
		window.aiInterval = setInterval(() => {
		  let coor = calculation(ballX, ballY, ballSpeedX, ballSpeedY);
		  ballIAX = coor[0];
		  ballIAY = coor[1];
		  //console.log("Posición actualizada de la pelota:");
		}, 1000);
	  }

	const h1Element = document.querySelector('#pong-container h1');
	  // Cambia el texto del h1
	h1Element.textContent = 'Single Player against I.A.';
	
	// cleanCanva();
	wait = true;
	// cDownState = true;
	deactivateKeydown();
	updateScore();
    gameLoop();
}



async function otraFuncion() {
    // Hacer algo asíncrono
	showWinMessage("3");
    await new Promise((resolve) => setTimeout(resolve, 800));
	showWinMessage("2");
	await new Promise((resolve) => setTimeout(resolve, 800));
	showWinMessage("1");
	await new Promise((resolve) => setTimeout(resolve, 800));
}

// Llamar a otraFuncion y luego ejecutar refresh
async function ejecutar() {
    await otraFuncion();
    refresh();
}

function handleSpacePress(event) {
    if (event.key === ' ') {
        initializeGameIA();
    }
}

function deactivateKeydown() {
	document.removeEventListener('keydown', handleSpacePress);
}

function gameLoop() {
	
	cleanCanva();
	drawCanva();
	updatePlayerAndBall();
	checkLowerAndUpperCollision();
	checkLeftAndRightCollision();
	moveAI();
	if (wait == true)
	{
		//timeoutId = setTimeout(refresh, 2000);
		if (finish) {
            terminateGameIA();
            
            // Añadimos el listener para la tecla 'space'
            document.addEventListener('keydown', handleSpacePress);
        }
		else
			ejecutar();
		wait = false;
	}
	else
		refresh();
}


function stopInterval() {
	if (window.aiInterval) {
	  clearInterval(window.aiInterval);
	  window.aiInterval = null; // Limpiar la referencia para evitar múltiples intervalos
	  console.log("Intervalo detenido.");
	}
  }

function drawRect(x, y, w, h, color) {
	ctx.fillStyle = color;
	ctx.fillRect(x, y, w, h);
}

function drawBall(x, y, size, color) {
	ctx.fillStyle = color;
	ctx.beginPath();
	ctx.arc(x, y, size, 0, Math.PI * 2);
	ctx.fill();
}

function drawIABall(x, y, size, color) {
	ctx.fillStyle = color;
	ctx.beginPath();
	ctx.arc(x, y, size, 0, Math.PI * 2);
	ctx.fill();
}

function cleanCanva()
{
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function drawCanva()
{
	drawRect(0, player1Y, PADDLE_WIDTH, PADDLE_HEIGHT, 'white');
	drawRect(canvas.width - PADDLE_WIDTH, player2Y, PADDLE_WIDTH, PADDLE_HEIGHT, 'white');
	drawBall(ballX, ballY, BALL_SIZE, 'white');
	//drawIABall(ballIAX, ballIAY, BALL_SIZE, 'green');
}

function updatePlayerAndBall()
{
	if (player1Up && player1Y > 0)
		player1Y -= PADDLE_SPEED;
	if (player1Down && player1Y < canvas.height -PADDLE_HEIGHT)
		player1Y += PADDLE_SPEED;
	if (player2Up && player2Y > 0)
		player2Y -= PADDLE_SPEED;
	if (player2Down && player2Y < canvas.height - PADDLE_HEIGHT)
		player2Y += PADDLE_SPEED;
	ballX += ballSpeedX;
	ballY += ballSpeedY;
}

function checkLowerAndUpperCollision()
{
	if (ballY - BALL_SIZE <= 0 || ballY + BALL_SIZE >= canvas.height)
		ballSpeedY = -ballSpeedY;
}


function leftCollision()
{
	if (ballX <= PADDLE_WIDTH) {
		if (ballY > player1Y && ballY < player1Y + (PADDLE_HEIGHT / 3))
		{
			ballSpeedX = -ballSpeedX;
			ballX += 0.5;
			console.log("y = ",  Math.abs(ballSpeedY).toFixed(3), " x = ",  Math.abs(ballSpeedX).toFixed(3));
			if (ballSpeedY <= 0)
			{
				if (Math.abs(ballSpeedY) < Math.abs(ballSpeedX))
				{
					ballSpeedY = ballSpeedY - ANGLE_INC;
					ballSpeedX = ballSpeedX - ANGLE_INC;
				}
			}
			else
			{
				ballSpeedY = ballSpeedY - ANGLE_INC;
				ballSpeedX = ballSpeedX + ANGLE_INC;
			}

		}
		else if (ballY > player1Y +  (PADDLE_HEIGHT / 3) && ballY < player1Y + ((PADDLE_HEIGHT / 3) * 2))
		{
			ballSpeedX = -ballSpeedX;
		}
		else if (ballY > player1Y + ((PADDLE_HEIGHT / 3) * 2) && ballY < player1Y + PADDLE_HEIGHT)
		{
			ballSpeedX = -ballSpeedX;
			ballX += 0.5;
			if (ballSpeedY <= 0)
			{
				ballSpeedY = ballSpeedY + ANGLE_INC;
				ballSpeedX = ballSpeedX + ANGLE_INC;
			}
			else
			{
				if(Math.abs(ballSpeedY) < Math.abs(ballSpeedX))
				{
					ballSpeedY = ballSpeedY + ANGLE_INC;
					ballSpeedX = ballSpeedX - ANGLE_INC;
				}
			}
		}
		else
		{
			player2Score++;
			if(player2Score == 3)
			{
				showWinMessage("You lose motherfucker!\nPush space to play again");
				finish = true;
			}
			updateScore();
			resetBall();
			resetPlayerPositions();
			wait = true;
			return;
		}
		ballSpeedX += SPEED_INC;
		if(ballSpeedY <= 0)
			ballSpeedY -= SPEED_INC;
		else
			ballSpeedY += SPEED_INC;
	}
}

function rightCollision()
{
	if (ballX >= canvas.width - PADDLE_WIDTH) {
		if (ballY > player2Y && ballY < player2Y + (PADDLE_HEIGHT / 3))
		{
			ballSpeedX = -ballSpeedX;
			ballX -= 0.5;
			console.log("y = ",  Math.abs(ballSpeedY).toFixed(3), " x = ",  Math.abs(ballSpeedX).toFixed(3));
			if (ballSpeedY <= 0)
			{
				if(Math.abs(ballSpeedY) < Math.abs(ballSpeedX))
				{
					ballSpeedY = ballSpeedY - ANGLE_INC;
					ballSpeedX = ballSpeedX + ANGLE_INC;
				}
			}
			else
			{
				ballSpeedY = ballSpeedY - ANGLE_INC;
				ballSpeedX = ballSpeedX - ANGLE_INC;	
			}
		}
		else if (ballY > player2Y + (PADDLE_HEIGHT / 3) && ballY < player2Y + ((PADDLE_HEIGHT / 3) * 2))
		{
			ballSpeedX = -ballSpeedX;
		}
		else if (ballY > player2Y + ((PADDLE_HEIGHT / 3) * 2) && ballY < player2Y + PADDLE_HEIGHT)
		{
			ballSpeedX = -ballSpeedX;
			ballX -= 0.5;
			console.log("y = ",  Math.abs(ballSpeedY).toFixed(3), " x = ",  Math.abs(ballSpeedX).toFixed(3));
			if (ballSpeedY <= 0)
			{
				ballSpeedY = ballSpeedY + ANGLE_INC;
				ballSpeedX = ballSpeedX - ANGLE_INC;
			}
			else
			{
				if (Math.abs(ballSpeedY) < Math.abs(ballSpeedX))
				{
					ballSpeedY = ballSpeedY + ANGLE_INC;
					ballSpeedX = ballSpeedX + ANGLE_INC;
				}
			}
		}
		else
		{
			player1Score++;
			if(player1Score == 3)
			{
				showWinMessage("You win!\nPush space to play again");
				finish = true;
			}
			updateScore();
			resetBall();
			resetPlayerPositions();
			wait = true;
			
			return;
		}
		ballSpeedX -= SPEED_INC;
		if(ballSpeedY <= 0)
			ballSpeedY -= SPEED_INC;
		else
			ballSpeedY += SPEED_INC;
	}
}

function checkLeftAndRightCollision()
{
	leftCollision();
	rightCollision();  
}

export function terminateGameIA() {
	
	document.removeEventListener('keydown', gameLoop);
	if (gameLoopId)
		cancelAnimationFrame(gameLoopId);
	if (timeoutId)
		clearTimeout(timeoutId);

	stopInterval();	

}

/* function showWinMessage(message) {
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	ctx.fillStyle = 'white';
	ctx.font = '30px Arial';
	ctx.textAlign = 'center';
	ctx.fillText(message, canvas.width / 2, canvas.height / 2);
} */

function showWinMessage(message) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
    ctx.font = '30px Arial';
    ctx.textAlign = 'center';

    // Dividimos el mensaje en líneas, usando "\n" como separador
    const lines = message.split('\n');
    
    // Para centrar cada línea verticalmente, ajustamos la posición Y para cada línea
    lines.forEach((line, index) => {
        ctx.fillText(line, canvas.width / 2, canvas.height / 2 + (index * 40)); // Ajusta el valor 40 para el espaciado entre líneas
    });
}

function resetBall()
{
	ballX = canvas.width / 2;
	ballY = canvas.height / 2;
	setBallSpeed();
}

function resetPlayerPositions()
{
	player1Y = (canvas.height - PADDLE_HEIGHT) / 2;
    player2Y = (canvas.height - PADDLE_HEIGHT) / 2;
	player2Down = false;
	player2Up = false;
}

function updateScore()
{
	document.getElementById('player1-score').textContent = 'Player 1: ' + player1Score;
	document.getElementById('player2-score').textContent = 'Player 2: ' + player2Score;
}

function refresh() {
	gameLoopId = requestAnimationFrame(gameLoop);
}

function getDirectionSideForBall()
{
	return Math.random() < 0.5 ? BALL_DIR_RIGHT : BALL_DIR_LEFT;
}

function getDirectionUpOrDownBall()
{
	return Math.random() < 0.5 ? BALL_DIR_UP : BALL_DIR_DOWN;
}

function setBallSpeed()
{
	let ballDirSideways = getDirectionSideForBall();
	let ballDirUpOrDown = getDirectionUpOrDownBall();
	ballSpeedX = 4;
	if (ballDirSideways == BALL_DIR_LEFT)
		ballSpeedX = (-1) * ballSpeedX;
	ballSpeedY = 1;
	if (ballDirUpOrDown == BALL_DIR_UP)
		ballSpeedY = (-1) * ballSpeedY;
}

//añadido para IA

function moveAI()
{
	/* if(player2Y >= ballIAY - 90  && player2Y <= ballIAY)
	{
		player2Up = false;
		player2Down = false;
	}
	if (player2Y < ballIAY - 90)
	{
		//player2Up = false;
		player2Down = true;
	}
	if (player2Y > ballIAY)
	{
		//player2Down = false;
		player2Up = true;
	} */

	
	if (player2Y < ballIAY - 90)// - 80
	{
		player2Up = false;
		player2Down = true;
	}
	if (player2Y > ballIAY )// - 10
	{
		player2Down = false;
		player2Up = true;
	}
}

function stopGame() {
    if (window.aiInterval) {
        clearInterval(window.aiInterval);
        window.aiInterval = null; // Reinicia la referencia para que no se pueda detener nuevamente
    }
}

// de aqui para abajo no se usa

function setBallForIA(){

	player2Up = false;
	player2Down = false;
	ballyIA = ballY;
}

function moveAIviejo() {
    console.log("Moviendo IA");
	//player2Up = false;
	//player2Down = false;
	if(ballyIA > player2Y + 50)
	{
		player2Down = true;
	}
	else
	{
		player2Up = true;
	}
	/* setTimeout(() => {
        player2Up = false;
        player2Down = false;
        console.log("Ambos valores ahora son false.");
    }, 22222200000); */
}



function startAI() {
    if (isAIRunning) {
        console.log("La IA ya está en ejecución");
        return;
    }
    console.log("Iniciando IA");
    IAstartTime = Date.now(); // Reiniciar el tiempo de inicio
    lastDirection = null; // Reiniciar la dirección
    if (!window.aiInterval) {
        window.aiInterval = setInterval(setBallForIA, 1000); // Ejecutar exactamente cada 1 segundo
    }
    isAIRunning = true;
}

function stopAI() {
    if (!isAIRunning) {
        console.log("La IA no está en ejecución");
        return;
    }
    console.log("Deteniendo IA");
    if (window.aiInterval) {
        clearInterval(window.aiInterval);
        window.aiInterval = null;
    }
    // Asegurarse de soltar ambas teclas al detener
    player2Up = false;
	player2Down = false;
    lastDirection = null;
    isAIRunning = false;
}



// Exponer funciones al ámbito global para pruebas manuales
window.startAI = startAI;
window.stopAI = stopAI;

console.log("app3.js ha terminado de cargarse");