from app import create_app, db
from app.models import Product

app = create_app()

with app.app_context():
    db.session.query(Product).delete()

    products = [
        Product(
            name='Camera 1',
            price=299.99,
            description='HD camera with zoom',
            image_url='/static/Products/Campic1.jpg',
            category='Cameras'
        ),
        Product(
            name='Camera 2',
            price=329.99,
            description='Waterproof digital camera',
            image_url='/static/Products/Campic2.jpg',
            category='Cameras'
        ),
        Product(
            name='Charger 1',
            price=19.99,
            description='Fast charger USB-C',
            image_url='/static/Products/charger1.jpg',
            category='Accessories'
        ),
        Product(
            name='Charger 2',
            price=17.99,
            description='Portable charger',
            image_url='/static/Products/charger2.jpg',
            category='Accessories'
        ),
        Product(
            name='Earphone 1',
            price=14.99,
            description='Wired earphones',
            image_url='/static/Products/earphone1.jpg',
            category='Audio'
        ),
        Product(
            name='Earphone 2',
            price=24.99,
            description='Wireless earbuds',
            image_url='/static/Products/earphone2.jpg',
            category='Audio'
        ),
        Product(
            name='External Drive 1',
            price=89.99,
            description='500GB external SSD',
            image_url='/static/Products/externaldrive1.jpg',
            category='Storage'
        ),
        Product(
            name='External Drive 2',
            price=119.99,
            description='1TB external SSD',
            image_url='/static/Products/externaldrive2.jpg',
            category='Storage'
        ),
        Product(
            name='Headphone 1',
            price=59.99,
            description='Over-ear wired headphones',
            image_url='/static/Products/headphone1.jpg',
            category='Audio'
        ),
        Product(
            name='Headphone 2',
            price=89.99,
            description='Bluetooth noise-cancelling headphones',
            image_url='/static/Products/headphone2.jpg',
            category='Audio'
        ),
        Product(
            name='Keyboard 1',
            price=49.99,
            description='Mechanical keyboard RGB',
            image_url='/static/Products/keybord1.jpg',
            category='Accessories'
        ),
        Product(
            name='Keyboard 2',
            price=69.99,
            description='Wireless mechanical keyboard',
            image_url='/static/Products/keyboard2.jpg',
            category='Accessories'
        ),
        Product(
            name='Laptop 1',
            price=899.99,
            description='Core i5, 8GB RAM, 256GB SSD',
            image_url='/static/Products/laptop1.jpg',
            category='Laptops'
        ),
        Product(
            name='Laptop 2',
            price=1199.99,
            description='Core i7, 16GB RAM, 512GB SSD',
            image_url='/static/Products/laptop2.jpg',
            category='Laptops'
        ),
        Product(
            name='Mobile 1',
            price=499.99,
            description='Smartphone with 64MP camera',
            image_url='/static/Products/mobilepic1.jpg',
            category='Mobiles'
        ),
        Product(
            name='Mobile 2',
            price=699.99,
            description='5G smartphone with AMOLED screen',
            image_url='/static/Products/mobilepic2.jpg',
            category='Mobiles'
        ),
        Product(
            name='Monitor',
            price=189.99,
            description='24" Full HD Monitor',
            image_url='/static/Products/monitor1.jpg',
            category='Displays'
        ),
        Product(
            name='Mouse 1',
            price=25.99,
            description='Wireless ergonomic mouse',
            image_url='/static/Products/mouse1.jpg',
            category='Accessories'
        ),
        Product(
            name='Mouse 2',
            price=34.99,
            description='Gaming mouse RGB',
            image_url='/static/Products/mouse2.jpg',
            category='Accessories'
        ),
        Product(
            name='Power Bank',
            price=29.99,
            description='10000mAh portable power bank',
            image_url='/static/Products/powerbang1.jpg',
            category='Accessories'
        ),
        Product(
            name='Tablet 1',
            price=349.99,
            description='10-inch Android tablet',
            image_url='/static/Products/tab1.jpg',
            category='Tablets'
        ),
        Product(
            name='Tablet 2',
            price=399.99,
            description='iOS tablet with Retina display',
            image_url='/static/Products/tab2.jpg',
            category='Tablets'
        ),
        Product(
            name='USB Hub',
            price=14.99,
            description='4-port USB hub',
            image_url='/static/Products/usbhub1.jpg',
            category='Accessories'
        ),
        Product(
            name='USB Hub 2',
            price=19.99,
            description='7-port USB hub with power',
            image_url='/static/Products/usbhub2.jpg',
            category='Accessories'
        )
    ]

    db.session.bulk_save_objects(products)
    db.session.commit()

    print("✅ All 22 products with correct images and categories added successfully.")
