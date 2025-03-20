# import sys
# sys.path.append('/Users/ridhamap/Python_wrapper_alchemy/alchemy-reimplemented/alchemy_new/lib/python3.12/site-packages')
# import alchemy

# def test_reactor():
#     print("Testing PyReactor:")
#     reactor = alchemy.PyReactor()
#     print("PyReactor instance created successfully.")

# def test_standardization():
#     print("Testing PyStandardization:")
#     try:
#         std = alchemy.PyStandardization("prefix")
#         print("Standardization created with 'prefix':", std)
#     except ValueError as e:
#         print("Error in creating Standardization:", e)
# """
# def test_soup():
#     print("Testing PySoup:")
#     soup = alchemy.PySoup()
#     print("Empty PySoup instance created.")
#     print("Initial length of soup:", soup.len())
    
#     valid_expressions = [
#     "λx.x", 
#     "λx.λy.xy", 
#     "(λx.x) y", 
#     "λx.λy.(yx)", 
#     "λf.λx.(f (f x))", 
#     "(λx.λy.(x y)) z", 
#     "λa.λb.(a (b b))", 
#     "λf.λg.λx.(f (g x))", 
#     "(λx.(λy.(x y))) z", 
#     "λm.λn.λf.(m (n f))", 
#     "λp.λq.λr.((p q) r)", 
#     "(λa.a a) (λb.b b)", 
#     "λx.λy.λz.((x z) (y z))", 
#     "λs.λz.(s (s z))", 
#     "(λx.(λy.(x (y y)))) (λx.(λy.(x y)))", 
#     "λm.λn.λo.(m (n o))", 
#     "λu.λv.λw.((u v) (w u))", 
#     "λx.λy.(x (λz.(y z)))", 
#     "λa.λb.λc.((a b) c)", 
#     "λx.(λy.(λz.((x y) z)))", 
#     "λx.λy.λz.λw.(((x y) (z w)))", 
#     "λf.λx.(f (f (f x)))", 
#     "λg.λh.λi.(g (h i))", 
#     "(λx.λy.(x (x y))) (λx.x)"
# ]

#     soup.perturb(valid_expressions)
    
#     print("Soup after perturbation:", soup.expressions())
#     print("Unique expressions:", soup.unique_expressions())
#     print("Population entropy:", soup.population_entropy())

# """
# def test_soup():
#     print("Testing PySoup with generated expressions from PyBTreeGen:")
#     soup = alchemy.PySoup()
#     print("Empty PySoup instance created.")
#     print("Initial length of soup:", soup.len())
    
#     # Generate expressions using PyBTreeGen
#     gen = alchemy.PyBTreeGen.from_config(5, 0.5, 3, alchemy.PyStandardization("prefix"))
#     generated_expressions = [gen.generate() for _ in range(150)]  # Generate 150 expressions
    
#     # Perturb the soup with generated expressions
#     soup.perturb(generated_expressions)
    
#     print("Soup after perturbation:", soup.expressions())
#     print("Unique expressions:", soup.unique_expressions())
#     print("Population entropy:", soup.population_entropy())

# def test_btree_gen():
#     print("Testing PyBTreeGen:")
#     # Change "postfix" to a supported type, such as "prefix"
#     gen = alchemy.PyBTreeGen.from_config(5, 0.5, 3, alchemy.PyStandardization("prefix"))
#     print("BTreeGen instance created.")
#     print("Generated expression:", gen.generate())
#     print("Generated 3 expressions:", gen.generate_n(3))


# def test_fontana_gen():
#     print("Testing PyFontanaGen:")
#     fontana_gen = alchemy.PyFontanaGen.from_config((0.1, 0.5), (0.2, 0.6), 5, 2)
#     print("FontanaGen instance created.")
#     result = fontana_gen.generate()
#     print("Generated expression from FontanaGen:", result)

# def test_utilities():
#     print("Testing Utilities:")
#     encoded = alchemy.encode_hex_py([104, 101, 108, 108, 111])
#     print("Encoded hex:", encoded)
#     try:
#         decoded = alchemy.decode_hex_py(encoded)
#         print("Decoded hex:", decoded)
#     except ValueError as e:
#         print("Error in decoding hex:", e)
# """
# def test_soup():
#     print("Testing PySoup with generated random expressions:")
#     soup = alchemy.PySoup()
#     soup.generate_random_expressions(100, 5)  # Generate 100 expressions with max depth 5

#     print("Soup length:", soup.len())
#     print("First 10 expressions:", list(soup.expressions())[:10])
# """


# def test_experiments():
#     print("Testing Experiment Functions:")
#     try:
    
#         #alchemy.run_look_for_add()
#         #print("run_look_for_add executed successfully.")
#         alchemy.run_entropy_series()
#         print("run_entropy_series executed successfully.")
#         alchemy.run_entropy_test()
#         print("run_entropy_test executed successfully.")
#         alchemy.run_sync_entropy_test()
#         print("run_sync_entropy_test executed successfully.")
#     except Exception as e:
#         print("Error in running experiment functions:", e)

# if __name__ == "__main__":
#     test_reactor()
#     test_standardization()
#     test_soup()
#     test_btree_gen()
#     test_fontana_gen()
#     test_utilities()
#     test_experiments()


