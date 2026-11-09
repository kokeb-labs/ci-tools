/**
 * @id kokeb/cpp20/result-type-not-nodiscard
 * @name KB-CPP-046: A Result type is declared [[nodiscard]]
 * @description A driver's Result type must be [[nodiscard]], so the compiler reports every call whose result
 *              is ignored (the matrix relies on it for MISRA C++:2023 Rule 0.1.2).
 * @kind problem
 * @precision very-high
 * @problem.severity error
 * @tags external/kokeb/id/kb-cpp-046
 *       external/kokeb/obligation/required
 *       scope/single-translation-unit
 */

import cpp

/** A class or class template the source defines under the name `Result`. */
class ResultType extends Class {
  ResultType() {
    this.getSimpleName() = "Result" and
    this.hasDefinition() and
    this.fromSource() and
    // The template, and each explicit specialisation, are checked once; implicit instantiations follow them.
    not this instanceof ClassTemplateInstantiation
  }
}

predicate isNodiscard(Class c) { c.getAnAttribute().getName() = "nodiscard" }

from ResultType r
where not isNodiscard(r)
select r, "Result type '" + r.getName() + "' is not declared [[nodiscard]] (KB-CPP-046)."
