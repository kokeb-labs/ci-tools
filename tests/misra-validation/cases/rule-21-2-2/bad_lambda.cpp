// Seeded violation: strchr called from a lambda in a template.
#include <cstring>

namespace kv::rule_21_2_2::bad_lambda {

template <typename F>
bool apply(F f, const char* text) {
  return f(text);
}

bool has_colon(const char* text) {
  return apply([](const char* t) { return std::strchr(t, ':') != nullptr; }, text);
}

}  // namespace kv::rule_21_2_2::bad_lambda
