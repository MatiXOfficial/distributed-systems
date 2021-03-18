package server;

import java.io.IOException;
import java.net.*;
import java.util.LinkedList;
import java.util.concurrent.Semaphore;

public class Server
{
    private final int serverPort;
    private ServerSocket serverSocket;
    private final LinkedList<ServerThreadTCP> serverThreadsTCP;
    private final Semaphore newThreadSemaphore;
    private int threadsCount;

    private ServerThreadUDP serverThreadUDP;
    private DatagramSocket datagramSocket;

    public Server(int serverPort)
    {
        this.serverPort = serverPort;
        serverThreadsTCP = new LinkedList<>();
        threadsCount = 0;
        newThreadSemaphore = new Semaphore(0);
    }

    // let the main server thread start a next thread
    public void startNextThread()
    {
        newThreadSemaphore.release();
    }

    public void deleteServerThread(ServerThreadTCP serverThreadTCP)
    {
        synchronized (serverThreadsTCP)
        {
            serverThreadsTCP.remove(serverThreadTCP);
        }
    }

    // message all clients except one that sent the message
    public void messageAllExceptTCP(ServerThreadTCP sendingThread, String message)
    {
        synchronized (serverThreadsTCP)
        {
            for (ServerThreadTCP serverThreadTCP : serverThreadsTCP)
            {
                if (serverThreadTCP != sendingThread)
                {
                    serverThreadTCP.sendMessage(sendingThread, message);
                }
            }
        }
    }

    // message all clients except one that sent the message
    public void messageAllExceptUDP(InetAddress address, int portNumber, String message)
    {
        synchronized (serverThreadsTCP)
        {
            for (ServerThreadTCP serverThreadTCP : serverThreadsTCP)
            {
                if (serverThreadTCP.checkAddress(address, portNumber) == false)
                {
                    serverThreadUDP.sendMessage(message, serverThreadTCP.getAddress(), serverThreadTCP.getPortNumber());
                }
            }
        }
    }

    public Socket acceptClient(ServerThreadTCP serverThreadTCP) throws IOException
    {
        Socket clientSocket = serverSocket.accept();
        synchronized (serverThreadsTCP)
        {
            serverThreadsTCP.push(serverThreadTCP);
        }
        return clientSocket;
    }

    public DatagramSocket getSocketUDP()
    {
        return datagramSocket;
    }

    private void startThreadTCP()
    {
        ServerThreadTCP serverThreadTCP = new ServerThreadTCP(this, ++threadsCount);
        serverThreadTCP.start();
    }

    private void startThreadUDP()
    {
        serverThreadUDP = new ServerThreadUDP(this);
        serverThreadUDP.start();
    }

    private void closeSockets()
    {
        try
        {
            if (datagramSocket != null)
            {
                datagramSocket.close();
            }
            if (serverSocket != null)
            {
                serverSocket.close();
            }
        }
        catch (IOException e)
        {
            System.out.println(e.getMessage());
        }
    }

    private void start()
    {
        System.out.println("Welcome to the SERVER!");
        // create sockets
        try
        {
            serverSocket = new ServerSocket(serverPort);
            datagramSocket = new DatagramSocket(serverPort);
            startThreadUDP();
            startThreadTCP();
        }
        catch (IOException e)
        {
            System.out.println(e.getMessage());
            closeSockets();
        }

        while(true)
        {
            // if one of the threads accepts a new clients, the semaphore will be released
            // and startThreadTCP() method will be called.
            try
            {
                newThreadSemaphore.acquire();
                System.out.println(serverThreadsTCP.size());
            }
            catch (InterruptedException e)
            {
                System.out.println(e.getMessage());
            }
            startThreadTCP();
        }
    }

    public static void main(String[] args)
    {
        if (args.length != 1)
        {
            System.out.println("Wrong number of arguments! Try: java Server <port number>");
            System.exit(1);
        }

        int serverPort = Integer.parseInt(args[0]);

        Server server = new Server(serverPort);
        server.start();
    }
}
