// Seeded violation: a rethrow in a helper, outside the handler that calls it.
namespace kv::rule_18_1_2::bad_helper {

void rethrow() { throw; }

int guard() {
  try {
    return 0;
  } catch (...) {
    rethrow();
  }
  return 1;
}

}  // namespace kv::rule_18_1_2::bad_helper
