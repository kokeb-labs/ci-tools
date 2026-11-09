// Compliant near miss: localeconv's result only read, through a pointer to const.
#ifndef KV_RULE_25_5_2_CONST_USE_OK_LOCALECONV_HPP
#define KV_RULE_25_5_2_CONST_USE_OK_LOCALECONV_HPP

#include <clocale>

namespace kv::rule_25_5_2_const_use::ok_localeconv {

[[nodiscard]] inline bool has_decimal_point() {
  const std::lconv* const conventions = std::localeconv();
  return (conventions != nullptr) && (conventions->decimal_point != nullptr);
}

}  // namespace kv::rule_25_5_2_const_use::ok_localeconv

#endif  // KV_RULE_25_5_2_CONST_USE_OK_LOCALECONV_HPP
