// Compliant: the environment string is only read, through a pointer to const.
#ifndef KV_RULE_25_5_2_SUBSCRIPT_WRITE_OK_HPP
#define KV_RULE_25_5_2_SUBSCRIPT_WRITE_OK_HPP

#include <cstdlib>

namespace kv::rule_25_5_2_subscript_write::ok {

[[nodiscard]] inline bool home_is_absolute() {
  const char* const home = std::getenv("HOME");
  return (home != nullptr) && (*home == '/');
}

}  // namespace kv::rule_25_5_2_subscript_write::ok

#endif  // KV_RULE_25_5_2_SUBSCRIPT_WRITE_OK_HPP
