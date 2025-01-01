from locust import HttpUser, task  # , between


class WebsiteUser(HttpUser):
    # wait_time = between(5, 15)

    # @task
    # def availability(self):
    #     self.client.get("/availability")

    @task
    def checkout(self):
        self.client.post("/checkout")
