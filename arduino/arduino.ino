/*
 *
 * author: feb 2019
 * Erick
 */

short int up_flag, eog;
unsigned long inicio, fim, tempo;
float up;
float lr;

void setup()
{
	Serial.begin(9600);
	Keyboard.begin();
	up_flag=0;
	eog=0;
}

void loop()
{
	if(Serial.available() > 0) {

		if(Serial.read() == 64){
			//Keyboard.write(218);
			Serial.println("Recebi");
			eog=1;

			while(eog){
				up = analogRead(2)*(5.0/1023.0);
				lr = analogRead(3)*(5.0/1023.0);
				//if(up>=2.0 && up_flag==0){
				//	up_flag=1;
				//	inicio = millis();
				//}

				//while(up_flag==1){
				//	up = analogRead(0)*(5.0/1023.0);
				//	if(up<=1.8){
				///		up_flag=0;
				//		fim = millis();
				//		tempo = fim - inicio;

				//Serial.println(tempo);
				//delay(1000);

				//		if(tempo<180){
				//			Serial.println("Blink");
				//			delay(1000);
				//		}

				//		else if(tempo>200){
				//			Serial.println("Up");
				//			Keyboard.write(218);
				//			eog=0;
				//			delay(1000); 
				//		}

				//	}

				//}


				if(lr>=2.5){
					Serial.println("Right");
					Keyboard.write(215);
					eog=0;
					delay(1000);
				}
				else if(lr<=0.8){
					Serial.println("Left");
					Keyboard.write(216);
					eog=0;
					delay(1000);
				}
				else if(up<=1.1){
					Serial.println("Down");
					Keyboard.write(217);
					eog=0;
					delay(1000);
				}
				else if(up>=2.5){
					Serial.println("up");
					eog=0;
					Keyboard.write(218);
					delay(1000);

				}

			}

		}
	}

}
