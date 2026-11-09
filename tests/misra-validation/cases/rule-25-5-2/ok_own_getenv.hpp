// Compliant near miss: a configuration lookup of our own named getenv, returning our own writable buffer.
#ifndef KV_RULE_25_5_2_OK_OWN_GETENV_HPP
#define KV_RULE_25_5_2_OK_OWN_GETENV_HPP

#include <array>

namespace kv::rule_25_5_2::ok_own_getenv {

[[nodiscard]] inline char* getenv(std::array<char, 8U>& store) { return store.data(); }

inline void set_first(std::array<char, 8U>& store) {
  char* value = getenv(store);
  *value = 'x';
}

}  // namespace kv::rule_25_5_2::ok_own_getenv

#endif  // KV_RULE_25_5_2_OK_OWN_GETENV_HPP
