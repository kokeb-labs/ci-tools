// Seeded violation: a string that the localeconv result points to written through a member pointer, even though
// the lconv object itself is held through a pointer to const.
#include <clocale>

namespace kv::rule_25_5_2::bad_lconv_member {

void scribble() {
  const std::lconv* const conventions = std::localeconv();  // seeded: clang-tidy
  if ((conventions != nullptr) && (conventions->grouping != nullptr)) {
    conventions->grouping[0] = 'x';  // seeded: codeql
  }
}

}  // namespace kv::rule_25_5_2::bad_lconv_member
