from locust import HttpUser, task, between
from random import randint

# When we run the test, locust creates an instance of this class to every user
class WebsiteUser(HttpUser):
    wait_time = between(1, 5) # between each task, locust is waiting 1-5 seconds


    @task(2) # Addid a weight of two to represent the importance (how likely this task gets executed)
    def view_products(self):
        collection_id = randint(2, 6)
        self.client.get(f'/store/products/?collection_id={collection_id}', 
                        name='/store/products')
        
    @task(4)
    def view_product(self):
        product_id = randint(1,1000)
        self.client.get(f'/store/products/{product_id}', name='/store/products/:id')

    @task(1)
    def add_to_cart(self):
        product_id = randint(1, 10) # Limiting the range to see if updating the product quantity has any performance issues
        self.client.post(
            f'/store/carts/{self.cart_id}/items/', 
            name='/store/carts/items',
            json={'product_id': product_id, 'quantity': 1}
        )


    def on_start(self): # Lifecycle hook - called every time a new user starts browing our website
        response = self.client.post('/store/carts/')
        results = response.json()
        self.cart_id = results['id']