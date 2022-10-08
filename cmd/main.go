package main

import (
	"context"
	"fmt"
	rkboot "github.com/rookie-ninja/rk-boot"
	"github.com/rookie-ninja/rk-grpc/boot"
	mlService "github.com/shar/vtb/data-api-vtb-backend/api/gen/v1"
	"google.golang.org/grpc"
	"log"
)

type GrpcClient struct {
	conn   *grpc.ClientConn
	client mlService.MlServiceClient
}

const SERVER_ADDR = "127.0.0.1:6000"

func InitGrpcConnection() (*GrpcClient, error) {
	conn, err := grpc.Dial(SERVER_ADDR, grpc.WithInsecure())

	if err != nil {
		log.Fatal(err)
	}

	client := mlService.NewMlServiceClient(conn)
	return &GrpcClient{conn, client}, nil

}

func (g *GrpcClient) Digest(role mlService.Role, path string) ([]string, error) {
	req := mlService.DigestRequest{
		Role: role,
		Path: path,
	}
	res, err := g.client.Digest(context.Background(), &req)
	if err != nil {
		return nil, err
	}
	return res.News, nil
}

func (g *GrpcClient) Trend(role mlService.Role, path string) ([]string, error) {
	req := mlService.TrendRequest{
		Role: role,
		Path: path,
	}

	res, err := g.client.Trend(context.Background(), &req)

	if err != nil {
		return nil, err
	}
	return res.Incites, nil
}

func registermlService(server *grpc.Server) {
	mlService.RegisterMlServiceServer(server, &mlServiceServer{})
}

type mlServiceServer struct{}

func (server *mlServiceServer) Digest(ctx context.Context, request *mlService.DigestRequest) (*mlService.DigestResponse, error) {

	client, err := InitGrpcConnection()

	if err != nil {
		fmt.Println(err)
	}

	news, _ := client.Digest(request.Role, request.Path)
	return &mlService.DigestResponse{News: news}, nil
}

func (server *mlServiceServer) Trend(ctx context.Context, request *mlService.TrendRequest) (*mlService.TrendResponse, error) {

	client, err := InitGrpcConnection()

	if err != nil {
		fmt.Println(err)
	}

	incites, _ := client.Trend(request.Role, request.Path)
	return &mlService.TrendResponse{Incites: incites}, nil

}

func main() {

	boot := rkboot.NewBoot()

	grpcEntry := boot.GetEntry("mlService").(*rkgrpc.GrpcEntry)

	grpcEntry.AddRegFuncGrpc(registermlService)

	grpcEntry.AddRegFuncGw(mlService.RegisterMlServiceHandlerFromEndpoint)

	boot.Bootstrap(context.Background())

	boot.WaitForShutdownSig(context.Background())
}
