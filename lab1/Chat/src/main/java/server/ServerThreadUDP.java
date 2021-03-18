package server;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.util.Arrays;

public class ServerThreadUDP extends Thread
{
    private Server server;

    public ServerThreadUDP(Server server)
    {
        this.server = server;
    }

    @Override
    public void run()
    {
        byte[] receiveBuffer = new byte[512];

        while(true)
        {
            Arrays.fill(receiveBuffer, (byte)0);

            try
            {
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                server.getSocketUDP().receive(receivePacket);
                String message = new String(receivePacket.getData(), 0, receivePacket.getLength());
                System.out.println("(UDP) Received a message:");
                System.out.println(message);
                server.messageAllExceptUDP(receivePacket.getAddress(), receivePacket.getPort(), message);
            }
            catch (IOException e)
            {
                System.out.println(e.getMessage());
            }
        }
    }

    public void sendMessage(String message, InetAddress address, int portNumber)
    {
        byte[] sendBuffer = message.getBytes();
        DatagramPacket sendPacket = new DatagramPacket(sendBuffer, sendBuffer.length, address, portNumber);
        try
        {
            server.getSocketUDP().send(sendPacket);
        }
        catch (IOException e)
        {
            System.out.println(e.getMessage());
        }
    }
}
