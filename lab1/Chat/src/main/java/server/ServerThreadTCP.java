package server;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;

public class ServerThreadTCP extends Thread
{
    private Server server;
    private int id;

    private Socket clientSocket;
    private PrintWriter out;
    private BufferedReader in;
    private String nickname;

    public ServerThreadTCP(Server server, int id)
    {
        this.server = server;
        this.id = id;
    }

    @Override
    public synchronized void run()
    {
        try
        {
            System.out.println("(TCP) Starting a new thread, id: " + id);
            clientSocket = server.acceptClient(this);
            server.startNextThread();

            out = new PrintWriter(clientSocket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

            nickname = in.readLine();
            System.out.println("(TCP, " + id + ") Connected with client: " + nickname);

            while (true)
            {
                String message = in.readLine();
                if (message == null)
                {
                    System.out.println("(TCP, " + id + ") The socket of " + nickname + " was closed.");
                    break;
                }
                System.out.println("(TCP, " + id + ") Received: \"" + message + "\" from " + nickname + ":");
                server.messageAllExceptTCP(this, message);
            }
        }
        catch (IOException e)
        {
            System.out.println("(TCP, " + id + ") Connection with " + nickname + " was lost.");
        }
        finally
        {
            closeSocket();
        }
    }

    public void sendMessage(ServerThreadTCP sendingThread, String message)
    {
        out.println(sendingThread.getNickname() + ": " + message);
    }

    // check if the address and portNumber from arguments are equal to address and portNumber of the socket of this thread
    public boolean checkAddress(InetAddress address, int portNumber)
    {
        return (clientSocket.getInetAddress().equals(address)) && (clientSocket.getPort() == portNumber);
    }

    public InetAddress getAddress()
    {
        return clientSocket.getInetAddress();
    }

    public int getPortNumber()
    {
        return clientSocket.getPort();
    }

    private String getNickname()
    {
        return nickname;
    }

    private void closeSocket()
    {
        if (clientSocket != null)
        {
            server.deleteServerThread(this);
            try
            {
                clientSocket.close();
            }
            catch (IOException e)
            {
                System.out.println(e.getMessage());
            }
        }
    }
}
