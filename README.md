# Hướng dẫn chạy file

## Cài đặt Docker và Docker Compose
- [Link hướng dẫn](https://medium.com/@piyushkashyap045/comprehensive-guide-installing-docker-and-docker-compose-on-windows-linux-and-macos-a022cf82ac0b)

## Chạy file trên macOS/Linux
1. Mở Terminal
2. Di chuyển đến thư mục chứa project: `cd đường-dẫn-đến-thư-mục`
3. Chạy script tự động: `./run.sh`

## Chạy file trên Windows
1. Cài đặt Docker Desktop cho Windows (theo hướng dẫn ở trên)
2. Nếu muốn sử dụng file batch script, tạo file `run.bat` với nội dung:
```batch
@echo off
echo Starting phone number processing...

docker-compose build
docker-compose up

echo Processing complete! Check the output directory for results.
pause
```

### Lưu ý quan trọng:
1. Docker Desktop phải được chạy trước khi nháy đúp vào file BAT
2. Các file Excel cần xử lý phải được đặt trong cùng thư mục với file [phonenumber.py](http://_vscodecontentref_/0)
3. Khi chạy lần đầu, quá trình có thể mất thời gian vì Docker cần tải về image Python và cài đặt các thư viện cần thiết

Cách này rất thuận tiện cho người dùng Windows vì họ có thể chạy ứng dụng chỉ với một cú nháy đúp chuột, không cần sử dụng terminal.

