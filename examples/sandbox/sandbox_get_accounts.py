import os

from t_tech.invest.grpc.utils.clients import Client


def main():
    token = os.environ["INVEST_TOKEN"]

    with Client(token) as client:
        accounts = client.sandbox.get_sandbox_accounts()
        print(accounts)


if __name__ == "__main__":
    main()
