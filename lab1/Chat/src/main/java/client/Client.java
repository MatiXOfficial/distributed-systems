package client;

import javax.xml.crypto.Data;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.*;
import java.util.Scanner;

public class Client
{
    private String hostName;
    private InetAddress address;
    private int portNumber;
    private InetAddress multicastAddress;
    private int multicastPort;
    private String nickname;
    private Socket socketTCP;
    private DatagramSocket socketUDP;
    private MulticastSocket socketMulticast;
    private Scanner scanner;

    public void closeSockets()
    {
        try
        {
            if (socketTCP != null)
            {
                socketTCP.close();
            }
            if (socketUDP != null)
            {
                socketUDP.close();
            }
            if (socketMulticast != null)
            {
                socketMulticast.close();
            }
        }
        catch (IOException e)
        {
            System.out.println(e.getMessage());
        }
    }

    public Client(String hostName, int portNumber, String multicastAddress, int multicastPort, String nickname)
    {
        try
        {
            this.hostName = hostName;
            this.portNumber = portNumber;
            this.multicastAddress = InetAddress.getByName(multicastAddress);
            this.multicastPort = multicastPort;
            this.nickname = nickname;
            this.socketTCP = null;
            this.socketUDP = null;
            this.socketMulticast = null;
            this.scanner = new Scanner(System.in);
        }
        catch (UnknownHostException e)
        {
            System.out.println(e.getMessage());
        }
    }

    public Socket getSocketTCP()
    {
        return socketTCP;
    }

    // read a few lines string from the console
    private String readString()
    {
        String line = scanner.nextLine();
        if (line.equals(".q"))
        {
            return "";
        }
        else
        {
            String nextLines = readString();
            if (nextLines.isEmpty())
            {
                return line;
            }
            else
            {
                return (line + "\n" + nextLines);
            }
        }
    }

    private void start()
    {
        System.out.println("Hello " + nickname + "!");
        // create sockets
        try
        {
            socketTCP = new Socket(hostName, portNumber);
            this.address = InetAddress.getByName(hostName);
            socketUDP = new DatagramSocket(socketTCP.getLocalPort());
            socketMulticast = new MulticastSocket(multicastPort);
            socketMulticast.joinGroup(new InetSocketAddress(multicastAddress, multicastPort), NetworkInterface.getByName("bge0"));
        }
        catch (IOException e)
        {
            System.out.println("Could not connect to the server.");
            System.exit(1);
        }

        System.out.println("Connected with the server.");
        System.out.println("Type EXIT to exit.");
        System.out.println("Type the option, and then type the message to send it to the other users.");
        System.out.println("For UDP, Type .q in a new line to finish typing the message.");
        System.out.println("Options: T - TCP, U - UDP, M - multicast (UDP)");

        try
        {
            PrintWriter outTCP = new PrintWriter(socketTCP.getOutputStream(), true);

            // send nickname
            outTCP.println(nickname);

            // listening threads
            ClientListenerTCP clientListenerTCP = new ClientListenerTCP(this);
            clientListenerTCP.start();

            ClientListenerUDP clientListenerUDP = new ClientListenerUDP(socketUDP, "UDP");
            clientListenerUDP.start();

            ClientListenerUDP clientListenerMulticast = new ClientListenerUDP(socketMulticast, "MUL");
            clientListenerMulticast.start();

            while(true)
            {
                String message = scanner.nextLine();
                if (message.equals("EXIT"))
                {
                    System.out.println("GOOD BYE!");
                    break;
                }
                else if (message.equals("T"))
                {
                    System.out.print("TCP >>> ");
                    outTCP.println(scanner.nextLine());
                }
                else if (message.equals("U"))
                {
                    System.out.println("UDP \\/");
                    byte[] sendBuffer = readString().getBytes();
                    DatagramPacket sendPacket = new DatagramPacket(sendBuffer, sendBuffer.length, address, portNumber);
                    socketUDP.send(sendPacket);
                }
                else if (message.equals("M"))
                {
                    System.out.println("MUL \\/");
                    byte[] sendBuffer = readString().getBytes();
                    DatagramPacket sendPacket = new DatagramPacket(sendBuffer, sendBuffer.length, multicastAddress, multicastPort);
                    socketMulticast.send(sendPacket);
                }
                else
                {
                    System.out.println("Wrong option! Use: T - TCP, U - UDP, M - multicast (UDP), EXIT - exit");
                    continue;
                }
                System.out.println("What's next? Use: T - TCP, U - UDP, M - multicast (UDP), EXIT - exit");
            }
        }
        catch (Exception e)
        {
            System.out.println("Server was closed.");
        }
        finally
        {
            closeSockets();
        }
    }

    public static void main(String[] args)
    {
        if (args.length != 5)
        {
            System.out.println("Wrong number of arguments! Try: java client.Client <host name> <port number> <multicast address> <multicast port> <your nickname>");
            System.exit(1);
        }

        String hostName = args[0];
        int portNumber = Integer.parseInt(args[1]);
        String multicastAddress = args[2];
        int multicastPort = Integer.parseInt(args[3]);
        String nickname = args[4];

        Client client = new Client(hostName, portNumber, multicastAddress, multicastPort, nickname);
        client.start();
    }
}
