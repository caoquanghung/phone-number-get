# Hướng dẫn chạy file

## Cài đặt Docker và Docker Compose
- [Link hướng dẫn](https://medium.com/@piyushkashyap045/comprehensive-guide-installing-docker-and-docker-compose-on-windows-linux-and-macos-a022cf82ac0b)

## Chạy file trên Windows
1. Cài đặt Docker Desktop cho Windows (theo hướng dẫn ở trên)
2. Click đúp vào file `run.bat` để chạy.

### Lưu ý quan trọng:
1. Docker Desktop phải được chạy trước khi nháy đúp vào file BAT
2. Các file Excel cần xử lý phải được đặt trong thư mục `/input` cùng với file [phonenumber.py](http://_vscodecontentref_/0)
3. Khi chạy lần đầu, quá trình có thể mất thời gian vì Docker cần tải về image Python và cài đặt các thư viện cần thiết


## Mở rộng cho nhiều file
1. Thêm các file có đuôi `.xlsx` vào thư mục `/input`.
2. Chạy file `run.bat`.
3. Kết quả sẽ được xuất ra trong folder `/output`.
