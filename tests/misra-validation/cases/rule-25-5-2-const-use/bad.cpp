// Seeded violation: the object returned by localeconv modified through a pointer to non-const.
#include <clocale>

namespace kv::rule_25_5_2_const_use::bad {

void clear_decimal_point() {
  std::lconv* conventions = std::localeconv();
  conventions->decimal_point = nullptr;
}

}  // namespace kv::rule_25_5_2_const_use::bad
