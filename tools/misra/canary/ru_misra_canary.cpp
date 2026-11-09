// ru-misra's canary: compiled into every scan's CodeQL database next to the caller's build, with known violations
// that the validated queries must report. If any is missing from the results, the scan did not really run (no
// tracing, wrong pack, empty suite) and ru-misra fails. Never part of the caller's results.
#include <cstdint>

std::int32_t ru_misra_canary_global = 0;  // Rule 6.0.3: a declaration in the global namespace

namespace ru_misra_canary {

template <typename T>
struct Result {  // KB-CPP-046: a Result type without [[nodiscard]]
  T value{};
};

std::int32_t pick(std::int32_t a, std::int32_t unused) {  // Rule 0.2.2: a named parameter never read
  std::int32_t total = ru_misra_canary_global;
  for (std::int32_t i = 0; i < a; ++i)  // Rule 9.3.1: a loop body that is not a compound statement
    total = i;
  return total;
}

}  // namespace ru_misra_canary
