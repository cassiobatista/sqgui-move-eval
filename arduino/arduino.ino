/*
 *
 * author: feb 2019
 * erick
 */

void setup()
{
	Serial.begin(9600);
}

void loop()
{
	if(Serial.available() > 0) 
		if(Serial.read() == 64)
			Serial.println("ok");
}
