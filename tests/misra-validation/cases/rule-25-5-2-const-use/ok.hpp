// Compliant: the environment string is only read, through a pointer to const.
#ifndef KV_RULE_25_5_2_CONST_USE_OK_HPP
#define KV_RULE_25_5_2_CONST_USE_OK_HPP

#include <cstdlib>

namespace kv::rule_25_5_2_const_use::ok {

[[nodiscard]] inline bool has_home() {
  const char* const home = std::getenv("HOME");
  return home != nullptr;
}

}  // namespace kv::rule_25_5_2_const_use::ok

#endif  // KV_RULE_25_5_2_CONST_USE_OK_HPP
