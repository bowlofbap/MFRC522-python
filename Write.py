import RPi.GPIO as GPIO
import MFRC522
import signal

def end_read(signal, frame):
    """Cleanup on exit."""
    print("Ctrl+C captured, ending read.")
    GPIO.cleanup()
    exit(0)

signal.signal(signal.SIGINT, end_read)

# Initialize the reader
MIFAREReader = MFRC522.MFRC522(dev_num=1)

while True:
    print("Waiting for card...")
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    if status == MIFAREReader.MI_OK:
        print("Card detected")
        (status, uid) = MIFAREReader.MFRC522_Anticoll()

        if status == MIFAREReader.MI_OK:
            print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
            MIFAREReader.MFRC522_SelectTag(uid)

            sector = 8
            print(f"Authenticating sector {sector}...")
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, sector, key, uid)

            if status == MIFAREReader.MI_OK:
                user_data = input("Enter 16 characters to write: ").ljust(16)[:16]
                data = [ord(c) for c in user_data[:16]]

                print(f"Writing to sector {sector}...")
                MIFAREReader.MFRC522_Write(sector, data)

                print("Verifying write...")
                MIFAREReader.MFRC522_Read(sector)

                MIFAREReader.MFRC522_StopCrypto1()
                break
            else:
                print("Authentication failed.")
