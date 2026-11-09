// Compliant near miss: the classic locale referred to explicitly, and a member named global; the global locale is left alone.
#ifndef KV_RULE_25_5_1_OK_LOCAL_HPP
#define KV_RULE_25_5_1_OK_LOCAL_HPP

#include <locale>

namespace kv::rule_25_5_1::ok_local {

struct Settings {
  bool use_classic{true};
  [[nodiscard]] bool global() const { return use_classic; }
};

[[nodiscard]] inline const std::locale* chosen(const Settings& s) {
  return s.global() ? &std::locale::classic() : nullptr;
}

}  // namespace kv::rule_25_5_1::ok_local

#endif  // KV_RULE_25_5_1_OK_LOCAL_HPP
