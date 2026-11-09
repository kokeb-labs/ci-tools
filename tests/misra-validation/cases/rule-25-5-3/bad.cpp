// Seeded violation: the first getenv result used after a second getenv call may have overwritten it.
#include <cstdlib>

namespace kv::rule_25_5_3::bad {

bool same_value() {
  const char* const first = std::getenv("FIRST");  // seeded: clang-tidy
  const char* const second = std::getenv("SECOND");  // seeded: clang-tidy
  return first == second;  // seeded: codeql
}

}  // namespace kv::rule_25_5_3::bad
