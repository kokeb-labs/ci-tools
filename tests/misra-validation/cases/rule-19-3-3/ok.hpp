// Compliant: the mixed-use macro is only given plain literals and names, never other macros.
#ifndef KV_RULE_19_3_3_OK_HPP
#define KV_RULE_19_3_3_OK_HPP

#include <cstdint>

#define KV_RULE_19_3_3_SHOW(X) kv::rule_19_3_3::ok::Entry{#X, (X)}

namespace kv::rule_19_3_3::ok {

struct Entry {
  const char* name;
  std::uint32_t value;
};

inline Entry limit() { return KV_RULE_19_3_3_SHOW(7U); }

[[nodiscard]] inline bool named(const Entry& e) { return (e.name != nullptr) && (e.value > 0U); }

}  // namespace kv::rule_19_3_3::ok

#undef KV_RULE_19_3_3_SHOW

#endif  // KV_RULE_19_3_3_OK_HPP
