package client;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class ClientListenerTCP extends Thread
{
    private final Client client;

    public ClientListenerTCP(Client client)
    {
        this.client = client;
    }

    @Override
    public void run()
    {
        try
        {
            BufferedReader in = new BufferedReader(new InputStreamReader(client.getSocketTCP().getInputStream()));
            while (true)
            {
                String message = in.readLine();
                if (message == null)
                {
                    System.out.println("Server was closed.");
                    System.exit(2);
                }
                System.out.println("(TCP) Received message from " + message);
            }
        }
        catch (IOException e)
        {
            System.out.println("Server was closed.");
            System.exit(2);
        }
        finally
        {
            client.closeSockets();
        }
    }
}
