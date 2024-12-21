# Main Document

Normal references:
[[valid_doc]]
![[real_image.png]]

```python
[[ignored_doc1]]
![[ignored_image1.png]]
```

Here's a valid reference: [[real_doc]]

```
[[ignored_doc4]]
![[ignored_image4.png]]
```

And another valid reference: ![[real_image2.png]]

~~~
[[ignored_doc5]]
![[ignored_image5.png]]
~~~

Here's some inline code: `[[ignored_doc1]]` and `![[ignored_image1.png]]`

And some more: ``[[ignored_doc2]]`` and ``![[ignored_image2.png]]``

Mixed with valid references: `[[ignored_doc3]]` but [[valid_doc]] and `![[ignored_image3.png]]` but ![[real_image.png]]
