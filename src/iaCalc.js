'use strict'

let canvas;
let coord;


export function calculation(ballX, ballY, ballSpeedX, ballSpeedY)
{
    canvas = document.getElementById('pongCanvas');
    //while(ballX < canvas.width)
   // {
	//console.log("ballX =", ballX.toFixed(3), " ballY", ballY.toFixed(3));
	//console.log("ballspeedX =", ballSpeedX.toFixed(3), " ballSpeedY", ballSpeedY.toFixed(3));
	while(true){
		while (ballX > 10 && ballX < canvas.width - 10 && ballY > 0 + 10 && ballY + 10 < canvas.height)
		{
			ballX += ballSpeedX;
			ballY += ballSpeedY;
			//console.log("ballX =", ballX.toFixed(3), " ballY", ballY.toFixed(3));
			//console.log("ballspeedX =", ballSpeedX.toFixed(3), " ballSpeedY", ballSpeedY.toFixed(3));
		}
		//console.log("----CAMBIO------------");
		if (ballX >= canvas.width - 10)
		{
			//console.log("ballY =", ballY.toFixed(3));
			//console.log("FUERA------------");
			//console.log("ballYret", ballY.toFixed(3));
			coord = [ballX, ballY];
			return coord;
		}
		if(ballX <= 10)
		{
			ballSpeedX = -ballSpeedX;
			//ballSpeedY = -ballSpeedY;
			ballX += ballSpeedX;
			ballY += ballSpeedY;
			if(ballX <= 10)
				ballX = 11;
		}
		if (ballY - 10 <= 0 || ballY + 10 >= canvas.height)
		{
			ballSpeedY = -ballSpeedY;
			ballX += ballSpeedX;
			ballY += ballSpeedY;
		}
	}
    //coord = [ballX, ballY];
    //return coord;
}