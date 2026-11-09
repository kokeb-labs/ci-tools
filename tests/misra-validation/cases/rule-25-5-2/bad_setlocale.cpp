// Seeded violation: the string returned by setlocale written through a pointer to non-const.
#include <clocale>

namespace kv::rule_25_5_2::bad_setlocale {

void scribble() {
  char* name = std::setlocale(LC_ALL, nullptr);  // seeded: clang-tidy
  if (name != nullptr) {
    *name = 'C';  // seeded: codeql
  }
}

}  // namespace kv::rule_25_5_2::bad_setlocale
