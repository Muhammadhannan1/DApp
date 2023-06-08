from django.shortcuts import render

# Create your views here.
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from web3 import Web3 ,utils
from .models import Product
from web3.exceptions import ContractLogicError, TransactionNotFound
from django.db import transaction
from DApp.seraializers import ProductSerializer

#w3 = Web3(Web3.HTTPProvider('http://localhost:7545')) 
#w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/woADNzUTgBUrY3thK2IC0Nahg7C1DYBr')) 
SMART_CONTRACT_ADDRESS = os.getenv('SMART_CONTRACT_ADDRESS')
COMPANY_ADDRESS =os.getenv('COMPANY_ADDRESS')
INFURA_URL = os.getenv('INFURA_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
infura_project_id = 'DApp Product'
w3 = Web3(Web3.HTTPProvider(INFURA_URL)) 
#print(w3.is_connected())

contract_address = SMART_CONTRACT_ADDRESS

contract_abi = [{"inputs":[{"internalType":"uint256","name":"productId","type":"uint256"}],"name":"getHash","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"products","outputs":[{"internalType":"uint256","name":"productId","type":"uint256"},{"internalType":"string","name":"productName","type":"string"},{"internalType":"string","name":"productDescription","type":"string"},{"internalType":"bytes32","name":"productHash","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"productId","type":"uint256"},{"internalType":"string","name":"productName","type":"string"},{"internalType":"string","name":"productDescription","type":"string"}],"name":"uploadProduct","outputs":[],"stateMutability":"nonpayable","type":"function"}]
util= utils
# Load Contract
contract = w3.eth.contract(address=contract_address,abi=contract_abi)

@api_view(['POST'])
def upload_product(request):
    data = request.data
    Name = data.get('name')
    Description = data.get('description')
    Price = data.get('price')
    subCategory = data.get('subcategory')

    if not Name:
        return Response({'success': False, 'error': 'Name field is required'}, status=400)
    if not Description:
        return Response({'success': False, 'error': 'Description field is required'}, status=400)
    if not Price:
        return Response({'success': False, 'error': 'Price field is required'}, status=400)
    if not subCategory:
        return Response({'success': False, 'error': 'subCategory field is required'}, status=400)    
    
    if len(Name) < 5:
        return Response({'success': False, 'error': 'Name should be at least 5 characters'}, status=400)

    if len(Description) < 10:
        return Response({'success': False, 'error': 'Description should be at least 10 characters'}, status=400)
    price = int(Price)
    if price  < 100:
        return Response({'success': False, 'error': 'Price value Should be at least 100'}, status=400) 
    try:

        product = Product(
        Name=Name,
        Description=Description,
        price = price,
        subCategory_id= subCategory
    )
        product.save()
        # Get the auto-generated product_id from the saved Product object
        product_id = product.id

        # Upload product and generate hash
        transaction = contract.functions.uploadProduct(
        product_id,
        Name,
        Description,
        ).build_transaction({
            'from': COMPANY_ADDRESS,
            'gas': 3000000,
            'gasPrice': w3.to_wei('50', 'gwei'),
            'nonce': w3.eth.get_transaction_count(COMPANY_ADDRESS),
               })
        signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
        '''
        transaction_receipt = w3.eth.get_transaction_receipt(transaction_hash)
        
        if transaction_receipt.status ==1:
            product.exists = True
            product.Hash = transaction_hash
            product.save()
            return Response({
            'success': True,
            'message': 'Product registered successfully',
            'transaction_hash': transaction_hash
        }, status=201)
        else:
            product.exists = False
            product.save()
            return Response({
            'success': True,
            'message': 'Product is unable to be registered on blockchain but it is saved in Database',
            'transaction_hash': None
        }, status=201)
       '''
        product.exists = True
        product.Hash = transaction_hash
        product.save()
        return Response({
        'success': True,
        'message': 'Product registered successfully',
        'transaction_hash': transaction_hash
    }, status=201)


    except ContractLogicError as e:
        # Handle contract logic errors
        return Response({'success': False, 'error': str(e)}, status=400)

    except TransactionNotFound as e:
        # Handle transaction not found errors
        return Response({'success': False, 'error': str(e)}, status=400)

    except Exception as e:
        # Handle other unexpected errors
        return Response({'success': False, 'error': 'An error occurred', 'e':str(e)}, status=500)


@api_view(['GET'])
def check_transaction(request, transaction_hash):
    # Retrieve the transaction details from the blockchain
    try:
        tx_receipt = w3.eth.get_transaction_receipt(transaction_hash)
       # print(tx_receipt.transactionHash)
        if tx_receipt is not None:
            # Transaction exists on the blockchain
            tx = w3.eth.get_transaction(transaction_hash)
            contract_function = contract.decode_function_input(tx['input'])
            contract_function_name = contract_function[0].fn_name
            contract_function_params = contract_function[1:]
           # ProductDetails = { 'Product Id':contract_function_params[0]['productId'],'Product Name':contract_function_params[0]['productName'],'Product Description':contract_function_params[0]['productDescription']}
            return Response({'success': True, 'message':'Product exists', 'Product Id':contract_function_params[0]['productId'],'Product Name':contract_function_params[0]['productName'],'Product Description':contract_function_params[0]['productDescription']}, status=200)
           # return Response({'success': True, 'message':'Product exists', 'data':ProductDetails}, status=200)
        else:
            # Transaction does not exist on the blockchain
            return Response({'success': False,'message':'Product Not Found', 'data':None}, status=200)
    except Exception as e:
        # Error occurred while checking the transaction
        return Response({'error': str(e)}, status=500)
    

@api_view(['GET'])
def get_products(request,subcatId):
    products = Product.objects.filter(subCategory_id=subcatId)
    serialized_products = ProductSerializer(products, many=True)
    print(products)
    print(serialized_products.data)
    if serialized_products.data:
        return Response({'success': True,'message':'Product Found ', 'data':serialized_products.data}, status=200)
    else:
        return Response({'success': False,'message':'No Product Found For This Category', 'data':None}, status=404)