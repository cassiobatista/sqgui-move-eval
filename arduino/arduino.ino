/*
 *
 * author: feb 2019
 * Erick
 */

void setup()
{
	Serial.begin(9600);
	Keyboard.begin();
}

void loop()
{
	if(Serial.available() > 0) 
		if(Serial.read() == 64){
			Keyboard.write(218);
			Serial.println("Up");
		}
}
