package client;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.util.Arrays;

public class ClientListenerUDP extends Thread
{
    private final DatagramSocket socket;
    private final String name;

    public ClientListenerUDP(DatagramSocket socket, String name)
    {
        this.socket = socket;
        this.name = name;
    }

    @Override
    public void run()
    {
        byte[] receiveBuffer = new byte[1024];

        while(true)
        {
            Arrays.fill(receiveBuffer, (byte)0);

            try
            {
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                socket.receive(receivePacket);
                String message = new String(receivePacket.getData(), 0, receivePacket.getLength());
                System.out.println("(" + name + ") Received a message: ");
                System.out.println(message);
            }
            catch (IOException e)
            {
                System.out.println(e.getMessage());
            }
        }
    }
}
