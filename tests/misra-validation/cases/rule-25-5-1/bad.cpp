// Seeded violation: the global locale changed at run time.
#include <clocale>
#include <locale>

namespace kv::rule_25_5_1::bad {

void use_c_locale() {
  static_cast<void>(std::setlocale(LC_ALL, "C"));  // seeded
  static_cast<void>(std::locale::global(std::locale::classic()));  // seeded
}

}  // namespace kv::rule_25_5_1::bad
