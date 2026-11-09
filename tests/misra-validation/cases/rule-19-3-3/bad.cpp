// Seeded violation: a parameter used both plainly and with #, given an argument that is itself a macro.
#include <cstdint>

#define KV_LIMIT 7U
#define KV_SHOW(x) kv::rule_19_3_3::bad::Entry{#x, (x)}  // seeded

namespace kv::rule_19_3_3::bad {

struct Entry {
  const char* name;
  std::uint32_t value;
};

Entry limit() { return KV_SHOW(KV_LIMIT); }

}  // namespace kv::rule_19_3_3::bad
