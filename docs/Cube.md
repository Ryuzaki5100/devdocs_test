# Generated Documentation with UML
## Cube Class Documentation

This documentation details the functions of the `Cube` class, explaining their functionality, dependencies, and business logic.

**Function 9: `Cube.getAlgorithm(String moves)`**

This function takes a string of moves (e.g., "RRRLLUUU") as input and converts it into a more human-readable algorithm format (e.g., ["R'", "L", "U'"]). It achieves this by condensing sequences of the same move into a single move with a modifier indicating the number of repetitions.

*   **Input:** A string `moves` representing a sequence of cube rotations.
*   **Output:** An `ArrayList<String>` representing the simplified algorithm.

**Explanation:**

1.  **Local Class `Temp`:**  A simple helper class is defined within `getAlgorithm` to store a character (move) and its repetition count.  This keeps track of consecutive moves efficiently.

    ```java
        class Temp {
            final char ch;
            final byte b;
            public Temp(char ch, byte b) {
                this.ch = ch;
                this.b = b;
            }
        }
    ```

2.  **Initialization:** A stack `s` of `Temp` objects is used to track consecutive moves. `v` holds the strings that represent repetitions(none, one, two or three repetitions). A `result` ArrayList is initialized to store the simplified moves.

3.  **Iterating Through Moves:** The function iterates through the input string `moves`.
    *   **New Move:** If the stack is empty or the current move is different from the move at the top of the stack, a new `Temp` object is created with a count of 1 and pushed onto the stack.
    *   **Existing Move:** If the current move is the same as the move at the top of the stack, the `Temp` object is popped from the stack, and if the count is not equal to 3 it increments the count in the `Temp` object. After incrementing the count it is pushed to the stack.
    If the count is 3 it is discarded and not pushed again onto the stack.

4.  **Building the Result:** After processing all moves, the stack is processed:
    *   Each `Temp` element is popped from the stack.
    *   The move character and repetitions are converted to string form, from `v`, and the `String` is appended to `result`. The move is appended to `result` using `add(0,...)` which means it is being added to the front of the `result` list.
    This process ensures that the output is in the correct order.

5.  **Return Value:** The function returns the `result` ArrayList.

**Example:**

```java
String moves = "RRRLLUUU";
ArrayList<String> algorithm = Cube.getAlgorithm(moves); // algorithm will be ["R'", "L", "U'"]
```

**Business Logic:** This function is useful for simplifying cube-solving algorithms, making them easier to read and execute. It's a core utility for representing move sequences efficiently.

**Function 8: `Cube.reverseAlgorithm(String s)`**

This function reverses a cube algorithm represented as a string, converting each move to its inverse (i.e., `R` becomes `R'`). It essentially inverts the order of moves and inverts the moves themselves.

*   **Input:** A string `s` representing a cube algorithm.
*   **Output:** A string representing the reversed algorithm.

**Explanation:**

1.  **Initialization:** A `StringBuilder` called `result` is created.
2.  **Invert Moves:** Loop through input, and convert each of the moves to inverted moves using the repeat method.
3.  **Reverse Algorithm:** The `result` is reversed using `new StringBuilder(result.toString()).reverse().toString();` and returned.

**Example:**

```java
String algorithm = "RUL";
String reversedAlgorithm = Cube.reverseAlgorithm(algorithm); // reversedAlgorithm will be "LUUUUUURRRRRR"
```

**Business Logic:** This function is crucial for solving a Rubik's Cube because many solutions rely on undoing a sequence of moves.  Knowing the reverse of an algorithm is fundamental to algorithms like commutators.

**Function 7: `Cube.execute(Cube c, String s)`**

This function simulates the execution of a cube algorithm on a given `Cube` object. It updates the cube's state based on the sequence of moves provided in the input string.

*   **Input:**
    *   `c`: A `Cube` object representing the initial state of the cube.
    *   `s`: A string representing the algorithm to execute.
*   **Output:** A new `Cube` object representing the cube's state after executing the algorithm.

**Explanation:**

1.  **Clone the Cube:** Creates a clone of the original cube to avoid modifying the original object.
2.  **Expand the Moves:** If the input algorithm string contains multiple moves (separated by space), the code expands any notation like "R2" or "R'" to "RR" or "RRR" respectively using a `StringBuilder`.
3.  **Iterate Through Moves:** The function then iterates through each character in the (possibly expanded) move string.
4.  **Update Edge:**
    *   For each move in the input string, it retrieves the `EdgePos` and `EdgeOrientation` from the temporary cube `temp`.
    *   It iterates through all 12 edges and updates their `EdgeOrientation` and `EdgePos` using pre-computed maps `nextEdgeOrientation` and `nextEdgePos`.
    *   `nextEdgeOrientation.get(ch).get(edgePos.getVal()[j]).get(edgeOrientation.getVal()[j])` fetches the new orientation value based on the move `ch`, the edge's current position `edgePos.getVal()[j]`, and its current orientation `edgeOrientation.getVal()[j]`.
    *   `nextEdgePos.get(ch).getVal()[edgePos.getVal()[j]]` fetches the new position value based on the move `ch` and the edge's current position `edgePos.getVal()[j]`.
    *   Finally, creates a new `Edge` with the updated `EdgePos` and `EdgeOrientation` and set it in the temporary cube.

5.  **Update Corner:**
    *   For each move in the input string, it retrieves the `CornerPos` and `CornerOrientation` from the temporary cube `temp`.
    *   It iterates through all 8 corners and updates their `CornerOrientation` and `CornerPos` using pre-computed maps `nextCornerOrientation` and `nextCornerPos`.
    *   `nextCornerOrientation.get(ch).get(cornerPos.getVal()[j]).get(cornerOrientation.getVal()[j])` fetches the new orientation value based on the move `ch`, the corner's current position `cornerPos.getVal()[j]`, and its current orientation `cornerOrientation.getVal()[j]`.
    *   `nextCornerPos.get(ch).getVal()[cornerPos.getVal()[j]]` fetches the new position value based on the move `ch` and the corner's current position `cornerPos.getVal()[j]`.
    *   Finally, creates a new `Corner` with the updated `CornerPos` and `CornerOrientation` and set it in the temporary cube.

6.  **Return Value:** The function returns the `temp` Cube.

**Example:**

```java
Cube solvedCube = new Cube(new Edge(), new Corner()); // Assuming default constructor creates a solved cube
Cube scrambledCube = Cube.execute(solvedCube, "R U R' U'");
```

**Business Logic:**  This is the core function that simulates cube moves. It allows you to apply algorithms and see their effect on the cube's state.

**Function 6: `Cube.clone()`**

This function creates a deep copy of a `Cube` object.

*   **Input:** None
*   **Output:** A new `Cube` object that is a copy of the original.

**Explanation:**

The function creates a new `Cube` object by calling the `Cube` constructor with clones of the original cube's `Edge` and `Corner` objects.

**Example:**

```java
Cube originalCube = new Cube(new Edge(), new Corner());
Cube clonedCube = originalCube.clone();
```

**Business Logic:** Creating copies of `Cube` objects is crucial when you want to perform operations on a cube without modifying the original. This is particularly important when exploring different solution paths or simulating moves.

**Function 5: `Cube.toString()`**

This function provides a string representation of the `Cube` object.

*   **Input:** None
*   **Output:** A string representation of the Cube.

**Explanation:**

It calls the `toString()` methods of the `Edge` and `Corner` objects.

**Example:**

```java
Cube myCube = new Cube(new Edge(), new Corner());
String cubeString = myCube.toString(); // cubeString will be something like: "Cube{edge=Edge{...}, corner=Corner{...}}"
```

**Business Logic:** Useful for debugging and displaying the cube's state.

**Function 4: `Cube.getEdge()`**

This function returns the `Edge` object associated with the `Cube`.

*   **Input:** None
*   **Output:** The `Edge` object.

**Explanation:** This function is a simple getter that returns the `edge` field of the `Cube` object.

**Example:**

```java
Cube myCube = new Cube(new Edge(), new Corner());
Edge edge = myCube.getEdge();
```

**Business Logic:**  Provides access to the `Edge` component of the `Cube`.

**Function 3: `Cube.setEdge(Edge edge)`**

This function sets the `Edge` object associated with the `Cube`.

*   **Input:** `edge`: The new `Edge` object to set.
*   **Output:** None

**Explanation:** This function is a simple setter that sets the `edge` field of the `Cube` object.

**Example:**

```java
Cube myCube = new Cube(new Edge(), new Corner());
Edge newEdge = new Edge();
myCube.setEdge(newEdge);
```

**Business Logic:** Allows modifying the `Edge` component of the `Cube`.

**Function 2: `Cube.setCorner(Corner corner)`**

This function sets the `Corner` object associated with the `Cube`.

*   **Input:** `corner`: The new `Corner` object to set.
*   **Output:** None

**Explanation:** This function is a simple setter that sets the `corner` field of the `Cube` object.

**Example:**

```java
Cube myCube = new Cube(new Edge(), new Corner());
Corner newCorner = new Corner();
myCube.setCorner(newCorner);
```

**Business Logic:** Allows modifying the `Corner` component of the `Cube`.

**Function 1: `Cube.getCorner()`**

This function returns the `Corner` object associated with the `Cube`.

*   **Input:** None
*   **Output:** The `Corner` object.

**Explanation:** This function is a simple getter that returns the `corner` field of the `Cube` object.

**Example:**

```java
Cube myCube = new Cube(new Edge(), new Corner());
Corner corner = myCube.getCorner();
```

**Business Logic:** Provides access to the `Corner` component of the `Cube`.

**Cyclomatic Complexity and Pain Points:**

*   **`Cube.execute()`:** This function has the highest cyclomatic complexity due to the nested loops and conditional logic involved in applying moves to both edges and corners. The numerous `get` calls on the `nextEdgeOrientation`, `nextEdgePos`, `nextCornerOrientation`, and `nextCornerPos` maps also increase the complexity and could potentially lead to performance bottlenecks if these maps are large.
*   **`Cube.getAlgorithm()`:** Uses a Stack which can be slightly complex to understand. The repeated modification of an ArrayList in the front of the list is less efficient than at the end.

**Possible Improvements:**

*   **`Cube.execute()`:** The nested loops in `execute` could be potentially optimized. The lookups in `nextEdgeOrientation`, `nextEdgePos`, `nextCornerOrientation` and `nextCornerPos` are performance-critical. Careful choice of data structures for these maps and potential caching could significantly improve performance. Consider using a more functional approach using streams which may improve readability.
*   **`Cube.getAlgorithm()`:** Using a `LinkedList` instead of `ArrayList` for `result` will be more efficient as adding at the front is a common operation.

## UML Diagram
![Image](images/Cube_img1.png)

