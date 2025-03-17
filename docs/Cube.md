# Generated Documentation with UML
```
## Cube Class Documentation

This document provides detailed documentation for the `Cube` class, outlining each function's purpose, implementation, and dependencies.

### 1. `Cube.getEdge()`

**Purpose:** This function serves as a getter method for the `edge` member variable of the `Cube` class. It retrieves the `Edge` object associated with the cube.

**Implementation:**

```java
public Edge getEdge() {
    return edge;
}
```

**Explanation:**  This is a straightforward getter method that returns the current `Edge` object of the `Cube` instance. It provides access to the cube's edge permutation and orientation information.

**Business Logic:** In the context of a Rubik's Cube simulation, the `Edge` object encapsulates the state of the 12 edges of the cube. This function allows other parts of the program to inspect the current edge configuration.

**Dependencies:** `edge` (instance variable of type `Edge`).

**Cyclomatic Complexity:** 1 (very low)

**Pain Points:** None. This is a simple getter.

### 2. `Cube.setEdge(Edge edge)`

**Purpose:** This function serves as a setter method for the `edge` member variable of the `Cube` class. It sets the `Edge` object associated with the cube to the provided `Edge` object.

**Implementation:**

```java
public void setEdge(Edge edge) {
    this.edge = edge;
}
```

**Explanation:** This is a setter method. It updates the `edge` member variable of the `Cube` object with the provided `edge` object.

**Business Logic:**  This function is crucial for modifying the state of the cube. When moves are applied, the edge permutation and orientation change, and this function is used to update the cube's internal representation of its edges.

**Dependencies:** `edge` (instance variable of type `Edge`), `Edge` (parameter of type `Edge`).

**Cyclomatic Complexity:** 1 (very low)

**Pain Points:** None. This is a simple setter.

### 3. `Cube.getCorner()`

**Purpose:** This function is a getter method for the `corner` member variable of the `Cube` class. It retrieves the `Corner` object associated with the cube.

**Implementation:**

```java
public Corner getCorner() {
    return corner;
}
```

**Explanation:** This method simply returns the value of the `corner` instance variable, allowing access to the `Corner` object representing the cube's corners.

**Business Logic:** Similar to `getEdge()`, this method allows access to the current configuration of the cube's corners.

**Dependencies:** `corner` (instance variable of type `Corner`).

**Cyclomatic Complexity:** 1 (very low)

**Pain Points:** None. This is a simple getter.

### 4. `Cube.setCorner(Corner corner)`

**Purpose:** This function is a setter method for the `corner` member variable of the `Cube` class. It sets the `Corner` object associated with the cube to the provided `Corner` object.

**Implementation:**

```java
public void setCorner(Corner corner) {
    this.corner = corner;
}
```

**Explanation:** This method sets the value of the `corner` instance variable to the `corner` object passed as a parameter.

**Business Logic:** Analogous to `setEdge()`, this function is used to update the cube's corner configuration after a move has been executed.

**Dependencies:** `corner` (instance variable of type `Corner`), `Corner` (parameter of type `Corner`).

**Cyclomatic Complexity:** 1 (very low)

**Pain Points:** None. This is a simple setter.

### 5. `Cube.clone()`

**Purpose:** Creates and returns a deep copy of the `Cube` object.

**Implementation:**

```java
public Cube clone() {
    return new Cube(this.getEdge().clone(), this.getCorner().clone());
}
```

**Explanation:** The `clone()` method creates a new `Cube` object and initializes it with deep copies of the current `Edge` and `Corner` objects. This ensures that changes to the cloned cube do not affect the original cube, and vice versa. The method calls `clone()` on the `Edge` and `Corner` objects to ensure that these are also deeply copied.

**Business Logic:** Cloning is essential when applying moves to a cube without modifying the original state.  The `execute` function relies on creating a clone of the cube before applying moves to simulate the changes.

**Dependencies:** `getEdge()`, `getCorner()`, `Edge.clone()`, `Corner.clone()`, `Cube` constructor.

**Cyclomatic Complexity:** 1 (very low)

**Pain Points:** Relies on `Edge` and `Corner` classes having correctly implemented `clone()` methods. If those methods perform shallow copies, then the cloned Cube will still share references to the same underlying `Edge` and `Corner` objects, leading to unexpected behavior.

### 6. `Cube.getAlgorithm(String moves)`

**Purpose:** This function simplifies a sequence of Rubik's Cube moves represented as a string. It converts repeated moves into a more concise format using "2" for double moves and "'" for inverse moves.

**Implementation:**

```java
public ArrayList<String> getAlgorithm(String moves) {
    class Temp {

        final char ch;

        final byte b;

        public Temp(char ch, byte b) {
            this.ch = ch;
            this.b = b;
        }
    }
    Stack<Temp> s = new Stack<>();
    ArrayList<String> v = new ArrayList<>(Arrays.asList("", "", "2", "'"));
    ArrayList<String> result = new ArrayList<>();
    for (int i = 0; i < moves.length(); i++) {
        if (s.isEmpty() || s.peek().ch != moves.charAt(i))
            s.push(new Temp(moves.charAt(i), (byte) 1));
        else {
            Temp x = s.pop();
            if (x.b != (byte) 3)
                s.push(new Temp(x.ch, (byte) (x.b + 1)));
        }
    }
    while (!s.isEmpty()) {
        Temp x = s.pop();
        if (x.b != 0)
            result.add(0, x.ch + v.get(x.b));
    }
    return result;
}
```

**Explanation:**
1.  **Inner Class `Temp`:**  A helper class `Temp` is defined to store a move character (`ch`) and its repetition count (`b`).

2.  **Initialization:**
    *   A `Stack<Temp>` called `s` is used to keep track of consecutive moves.
    *   An `ArrayList<String>` called `v` is initialized to store the move notations ("", "", "2", "'").  The indices of this list correspond to the repetition count in the `Temp` object.

3.  **Move Processing Loop:** The code iterates through the input `moves` string:
    *   If the stack is empty or the current move is different from the move at the top of the stack, a new `Temp` object is created with a repetition count of 1 and pushed onto the stack.
    *   If the current move is the same as the move at the top of the stack, the top `Temp` object is popped. If its repetition count is not 3 (meaning it's not an inverse move yet), a new `Temp` object is created with an incremented repetition count and pushed back onto the stack.

4.  **Result Construction Loop:** After processing all moves, the code iterates through the stack (in reverse order due to the stack's LIFO nature):
    *   For each `Temp` object popped from the stack, if the repetition count is not 0, the move character and its corresponding notation from the `v` list are concatenated and added to the beginning of the `result` list.

**Business Logic:** This function aims to represent a series of Rubik's Cube moves in a more compact and readable format. For instance, "RRR" is simplified to "R'", and "RR" becomes "R2". This is useful for displaying algorithms and sequences of moves.

**Dependencies:** `Stack`, `ArrayList`, `Arrays.asList()`.

**Cyclomatic Complexity:**  Moderate.  The main loop has an if-else, and the final loop adds complexity. Estimated around 5-7.

**Pain Points:**
*   The inner class `Temp` adds some overhead, although it's relatively minor.
*   The logic for determining inverse moves ("'") could be made clearer.
*   The use of indices into the `v` list can be a bit confusing.
*   The stack-based approach is functional but might not be the most intuitive for all readers.

**Example:**

```java
Cube cube = new Cube();
String moves = "RRRUUFFFRRRLL";
ArrayList<String> simplified = cube.getAlgorithm(moves);
System.out.println(simplified); // Output: [R', U2, F', L2]
```

### 7. `Cube.reverseAlgorithm(String s)`

**Purpose:** This function reverses a Rubik's Cube algorithm represented as a string by inverting each move three times and reversing the order of the moves.

**Implementation:**

```java
public String reverseAlgorithm(String s) {
    StringBuilder result = new StringBuilder();
    for (int i = 0; i < s.length(); i++) result.append(String.valueOf(s.charAt(i)).repeat(3));
    return new StringBuilder(result.toString()).reverse().toString();
}
```

**Explanation:**

1.  **Triple Each Move:** The function iterates through the input string `s` (representing the algorithm). For each character (move), it appends the character three times to the `result` StringBuilder.  This effectively inverts each move since applying a move three times is the same as applying its inverse.
2.  **Reverse the String:**  The `result` StringBuilder is then converted to a `String`, and a new `StringBuilder` is created with this string.  The `reverse()` method of the `StringBuilder` class is used to reverse the order of the moves.
3.  **Return Reversed Algorithm:** The reversed string is then returned.

**Business Logic:** In Rubik's Cube solving, it's often useful to reverse an algorithm to undo the changes it made. This function provides a simple way to generate the reverse of a sequence of moves. It relies on the fact that applying a move four times brings the cube back to its original state, so three repetitions are equivalent to the inverse of that move.

**Dependencies:** `StringBuilder`, `String.valueOf()`, `String.repeat()`.

**Cyclomatic Complexity:** 1 (very low).

**Pain Points:**

*   This function only works correctly if the input string `s` contains only basic moves (R, L, U, D, F, B).  It doesn't handle moves with "2" or "'" notations.
*   The implementation is a bit inefficient due to the repeated string concatenations.

**Example:**

```java
Cube cube = new Cube();
String algorithm = "RUF";
String reversedAlgorithm = cube.reverseAlgorithm(algorithm);
System.out.println(reversedAlgorithm); // Output: FUURR
```

### 8. `Cube.execute(Cube c, String s)`

**Purpose:** This function simulates the execution of a sequence of Rubik's Cube moves on a given `Cube` object.

**Implementation:**

```java
public Cube execute(Cube c, String s) {
    Cube temp = c.clone();
    String[] moves = s.split(" ");
    if (moves.length > 1) {
        StringBuilder sBuilder = new StringBuilder();
        for (String string : moves) {
            if (string.length() == 1)
                sBuilder.append(string.charAt(0));
            else if (string.charAt(1) == '2')
                sBuilder.append(String.valueOf(string.charAt(0)).repeat(2));
            else
                sBuilder.append(String.valueOf(string.charAt(0)).repeat(3));
        }
        s = sBuilder.toString();
    }
    for (int i = 0; i < s.length(); i++) {
        char ch = s.charAt(i);
        EdgePos edgePos = temp.getEdge().getEdgePos().clone();
        EdgeOrientation edgeOrientation = temp.getEdge().getEdgeOrientation().clone();
        for (int j = 0; j < 12; j++) {
            edgeOrientation.setVal(j, nextEdgeOrientation.get(ch).get(edgePos.getVal()[j]).get(edgeOrientation.getVal()[j]));
            edgePos.setVal(j, nextEdgePos.get(ch).getVal()[edgePos.getVal()[j]]);
        }
        temp.setEdge(new Edge(edgePos, edgeOrientation));
        CornerPos cornerPos = temp.getCorner().getCornerPos().clone();
        CornerOrientation cornerOrientation = temp.getCorner().getCornerOrientation().clone();
        for (int j = 0; j < 8; j++) {
            cornerOrientation.setVal(j, nextCornerOrientation.get(ch).get(cornerPos.getVal()[j]).get(cornerOrientation.getVal()[j]));
            cornerPos.setVal(j, nextCornerPos.get(ch).getVal()[cornerPos.getVal()[j]]);
        }
        temp.setCorner(new Corner(cornerPos, cornerOrientation));
    }
    return temp;
}
```

**Explanation:**

1.  **Clone the Cube:** The input `Cube c` is cloned to create a temporary `Cube temp` on which the moves will be applied. This ensures the original cube remains unchanged.

2.  **Parse and Process Moves:**

    *   The input string `s` containing moves is split by spaces. This handles algorithms like `"R U R'"`.
    *   The code then iterates through the split moves.  It converts the string into a single string where `'2'` is converted to repeating the move two times and `'` (inverse or prime) is converted to repeating the move three times. `"R2 U' F"` is converted to `"RRUUUF"`.

3.  **Apply Moves:** The code iterates through the simplified move string. For each move character `ch`:
    *   **Edge Transformation:**
        *   Clones `EdgePos` and `EdgeOrientation` from the `temp` cube's edge.
        *   Iterates through the 12 edges.  For each edge, it updates both the position and orientation.  It uses lookup tables `nextEdgePos` and `nextEdgeOrientation` to determine the new position and orientation based on the current move `ch`. These tables are indexed by move character, current edge position, and current edge orientation, respectively.
        *   Creates a new `Edge` object with the updated `EdgePos` and `EdgeOrientation` and sets it on the `temp` cube.
    *   **Corner Transformation:**
        *   Clones `CornerPos` and `CornerOrientation` from the `temp` cube's corner.
        *   Iterates through the 8 corners. For each corner, it updates both the position and orientation using lookup tables `nextCornerPos` and `nextCornerOrientation` in a similar way to how edges are handled.
        *   Creates a new `Corner` object with the updated `CornerPos` and `CornerOrientation` and sets it on the `temp` cube.

4.  **Return Modified Cube:** Finally, the modified `temp` cube is returned.

**Business Logic:** This function is the core of the Rubik's Cube simulation.  It allows you to apply a sequence of moves to a cube and observe the resulting state.  The use of lookup tables (`nextEdgePos`, `nextEdgeOrientation`, `nextCornerPos`, `nextCornerOrientation`) makes the move execution efficient.

**Dependencies:** `clone()`, `getEdge()`, `setEdge()`, `getCorner()`, `setCorner()`, `Edge.getEdgePos()`, `Edge.getEdgeOrientation()`, `Corner.getCornerPos()`, `Corner.getCornerOrientation()`, `EdgePos.clone()`, `EdgeOrientation.clone()`, `CornerPos.clone()`, `CornerOrientation.clone()`, `EdgePos.setVal()`, `EdgeOrientation.setVal()`, `CornerPos.setVal()`, `CornerOrientation.setVal()`, `Edge`, `Corner`, `nextEdgePos`, `nextEdgeOrientation`, `nextCornerPos`, `nextCornerOrientation`.

**Cyclomatic Complexity:** High. The function involves nested loops and conditional statements (primarily due to parsing the string).  The complexity is likely in the range of 10-15 or higher.

**Pain Points:**

*   **Lookup Tables:** The reliance on external lookup tables (`nextEdgePos`, `nextEdgeOrientation`, `nextCornerPos`, `nextCornerOrientation`) makes the code less self-contained and harder to understand without knowing the structure and contents of those tables. A more object-oriented approach (e.g., defining a `Move` class with methods to apply the move to `Edge` and `Corner` objects) could improve readability.
*   **Cloning:** The repeated cloning of `EdgePos`, `EdgeOrientation`, `CornerPos`, and `CornerOrientation` in each iteration of the move loop could be a performance bottleneck. Consider whether these clones are truly necessary or if the objects can be modified in place.
*   **String Parsing:** The string parsing logic could be improved for readability and robustness. It currently handles only single-character moves and '2' and `'` modifiers.
*   **Error Handling:** There is no error handling for invalid move characters or malformed input strings.
*   **Mutable State:** The repeated calls to `setVal()` methods on the cloned position and orientation objects suggest that the objects' internal state is being modified. If the classes which are using these methods, do not account for it, it can lead to unexpected behaviours

### 9. `Cube.toString()`

**Purpose:** Returns a string representation of the `Cube` object, including the string representations of its `Edge` and `Corner` objects.

**Implementation:**

```java
public String toString() {
    return "Cube{\n" + "edge=" + edge.toString() + ",\ncorner=" + corner.toString() + "\n}";
}
```

**Explanation:**

This method overrides the default `toString()` method of the `Object` class. It constructs a string that includes the class name ("Cube") and the string representations of the `edge` and `corner` member variables, obtained by calling their respective `toString()` methods.

**Business Logic:** This method is useful for debugging and displaying the state of the cube. It provides a human-readable representation of the cube's internal data.

**Dependencies:** `edge.toString()`, `corner.toString()`.

**Cyclomatic Complexity:** 1 (very low).

**Pain Points:** Relies on `Edge` and `Corner` classes having properly implemented `toString()` methods. If `Edge` and `Corner` classes have toString() methods that are poorly implemented, this Cube's toString method will also produce less-than-useful information. Also, the formatting of the output String is fixed, therefore it is not possible to customize it as needed.
```
## UML Diagram
![Image](images/Cube_img1.png)

