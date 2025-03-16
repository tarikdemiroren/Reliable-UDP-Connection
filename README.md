## 📡 Running the Receiver and Sender

### Start the Receiver and then the Sender
Run the receiver using the following format:  

```sh
python3 receiver.py <IP> <Port> <packet_loss_probability> <max_packet_delay>
python3 sender.py <file_path> <receiver_port> <window_size_N> <retransmission_timeout>
```

Example Usage
```sh
python3 receiver.py 127.0.0.1 8080 0.1 100
python3 Sender myfile.txt 8080 5 200
```

The demo will automatically send a file with the name <image.png> that is in the same directory as the sender.py
