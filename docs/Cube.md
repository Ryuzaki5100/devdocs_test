# Generated Documentation with UML
```java
/**
 * Documentation for the Cube class and its methods.
 * This class represents a Rubik's Cube and provides functionalities to manipulate and query its state.
 */

/**
 * Represents a Rubik's Cube with its edges and corners.
 */
class Cube {

    private Edge edge;
    private Corner corner;

    /**
     * Sets the corner configuration of the cube.
     * @param corner The new corner configuration.
     */
    public void setCorner(Corner corner) {
        this.corner = corner;
    }

    /**
     * Sets the edge configuration of the cube.
     * @param edge The new edge configuration.
     */
    public void setEdge(Edge edge) {
        this.edge = edge;
    }

    /**
     * Gets the current edge configuration of the cube.
     * @return The edge configuration.
     */
    public Edge getEdge() {
        return edge;
    }

    /**
     * Gets the current corner configuration of the cube.
     * @return The corner configuration.
     */
    public Corner getCorner() {
        return corner;
    }

    /**
     * Creates a deep copy of the Cube object.
     * It clones both the edge and corner configurations to ensure that the new Cube
     * object is independent of the original.
     *
     * @return A new Cube object that is a deep copy of the original.
     */
    public Cube clone() {
        return new Cube(this.getEdge().clone(), this.getCorner().clone());
    }

    /**
     * Executes a sequence of moves on a given Cube object.
     * It parses the move string, applies each move to the cube, and returns the resulting cube.
     *
     * @param c The Cube object to execute the moves on.
     * @param s The string representing the sequence of moves to execute.  Moves can be single letters (e.g., "R", "U"),
     *          or include modifiers like "2" (double move) or "'" (inverse move).  Examples: "R U", "R2 F'", "R U2 R'".
     * @return A new Cube object representing the result of applying the moves.
     */
    public Cube execute(Cube c, String s) {
        Cube temp = c.clone();
        String[] moves = s.split(" ");

        // Handle multi-move strings like "R U2 R'" by collapsing them to a simpler format "RUUURRR"
        if (moves.length > 1) {
            StringBuilder sBuilder = new StringBuilder();
            for (String string : moves) {
                if (string.length() == 1)
                    sBuilder.append(string.charAt(0));
                else if (string.charAt(1) == '2')
                    sBuilder.append(String.valueOf(string.charAt(0)).repeat(2));
                else
                    sBuilder.append(String.valueOf(string.charAt(0)).repeat(3)); // Inverse move is 3 times the original
            }
            s = sBuilder.toString();
        }

        // Apply each move to the cube
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);

            // Clone edge configuration
            EdgePos edgePos = temp.getEdge().getEdgePos().clone();
            EdgeOrientation edgeOrientation = temp.getEdge().getEdgeOrientation().clone();

            // Update edge positions and orientations based on the move
            for (int j = 0; j < 12; j++) {
                edgeOrientation.setVal(j, nextEdgeOrientation.get(ch).get(edgePos.getVal()[j]).get(edgeOrientation.getVal()[j]));
                edgePos.setVal(j, nextEdgePos.get(ch).getVal()[edgePos.getVal()[j]]);
            }
            temp.setEdge(new Edge(edgePos, edgeOrientation));

            // Clone corner configuration
            CornerPos cornerPos = temp.getCorner().getCornerPos().clone();
            CornerOrientation cornerOrientation = temp.getCorner().getCornerOrientation().clone();

            // Update corner positions and orientations based on the move
            for (int j = 0; j < 8; j++) {
                cornerOrientation.setVal(j, nextCornerOrientation.get(ch).get(cornerPos.getVal()[j]).get(cornerOrientation.getVal()[j]));
                cornerPos.setVal(j, nextCornerPos.get(ch).getVal()[cornerPos.getVal()[j]]);
            }
            temp.setCorner(new Corner(cornerPos, cornerOrientation));
        }
        return temp;
    }

    /**
     * Reverses a given algorithm string.  It triples each character in the input string,
     * reverses the resulting string, and returns the reversed string.
     *
     * @param s The algorithm string to reverse.  For example, "RU" represents Right then Up.
     * @return The reversed algorithm string.  For example, "RU" becomes "UUURRR".
     */
    public String reverseAlgorithm(String s) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < s.length(); i++)
            result.append(String.valueOf(s.charAt(i)).repeat(3));
        return new StringBuilder(result.toString()).reverse().toString();
    }

    /**
     * Converts a move sequence string into a simplified and standardized representation.
     * It handles moves with single quotes ('), and double moves (2). The logic simplifies input like RRR into R', RR into R2
     *
     * @param moves The string representing the sequence of moves (e.g., "R U R'").
     * @return An ArrayList of strings, where each string represents a single move with its modifier (e.g., ["R", "U", "R'"]).
     */
    public ArrayList<String> getAlgorithm(String moves) {
        // Local class to store character and byte information for move simplification.
        class Temp {
            final char ch;
            final byte b;

            public Temp(char ch, byte b) {
                this.ch = ch;
                this.b = b;
            }
        }

        Stack<Temp> s = new Stack<>();
        ArrayList<String> v = new ArrayList<>(Arrays.asList("", "", "2", "'")); // Mapping for move modifiers
        ArrayList<String> result = new ArrayList<>();

        for (int i = 0; i < moves.length(); i++) {
            // Push to stack if the stack is empty OR top element is different
            if (s.isEmpty() || s.peek().ch != moves.charAt(i))
                s.push(new Temp(moves.charAt(i), (byte) 1));
            else {
                // If the same move appears consecutively, increment the byte counter
                Temp x = s.pop();
                if (x.b != (byte) 3) // Max value = 3
                    s.push(new Temp(x.ch, (byte) (x.b + 1)));
            }
        }

        // Build the final result list
        while (!s.isEmpty()) {
            Temp x = s.pop();
            if (x.b != 0)
                result.add(0, x.ch + v.get(x.b)); // Prepend the move to the result list
        }
        return result;
    }

    /**
     * Returns a string representation of the Cube object, including its edge and corner configurations.
     *
     * @return A string representation of the Cube.
     */
    @Override
    public String toString() {
        return "Cube{\n" + "edge=" + edge.toString() + ",\ncorner=" + corner.toString() + "\n}";
    }
}

/**
 *  Business Logic:
 *  - The Cube class models the state of a Rubik's Cube.
 *  - `execute()` method simulates the application of a series of moves.
 *  - `reverseAlgorithm()` provides a utility for reversing move sequences, essential in solving algorithms.
 *  - `getAlgorithm()` simplify move sequences to a standard format.
 *  - The Edge and Corner classes would hold the actual permutation data and are essential parts of the cube state.
 */

 /**
  * Analysis:
  *
  * Cyclomatic Complexity:
  * - `execute()`: High due to multiple nested loops and conditional statements for move parsing and execution. The complexity
  *   arises from the conditional logic for handling moves with different modifiers (2, ') and the nested loops for updating
  *   edge and corner positions and orientations.
  * - `getAlgorithm()`: Moderate, due to the loop and conditional logic for simplifying the move sequence.
  * - `reverseAlgorithm()`: Low, as it contains a single loop and simple string manipulation.
  * - Other methods: Low, as they are simple getter/setter or cloning operations.
  *
  * Pain Points:
  * - The `execute()` method is complex and hard to read due to the nested loops and conditional statements.
  *   The reliance on magic numbers (e.g., 12 for edges, 8 for corners) and the complex logic for updating
  *   edge and corner orientations make it difficult to understand and maintain. The external dependency on `nextEdgePos`, `nextEdgeOrientation`,
  *  `nextCornerPos`, and `nextCornerOrientation` makes it even more harder to understand.
  * - The `getAlgorithm()` method could be more readable with better variable names and more comments.
  *
  * Possible Improvements:
  * - `execute()`:
  *   - Break down the method into smaller, more manageable functions. For example, create separate functions for
  *     parsing the move string, updating edge positions, updating edge orientations, updating corner positions, and
  *     updating corner orientations.
  *   - Use more descriptive variable names.
  *   - Replace magic numbers with named constants.
  *   - Consider using a data structure (e.g., a map) to store the move logic instead of nested loops and conditional statements.
  *   - Use design patterns such as the Command Pattern to encapsulate moves.
  * - `getAlgorithm()`: Use clearer variable names.
  */
```
## UML Diagram
![Image](images/Cube_img1.png)

